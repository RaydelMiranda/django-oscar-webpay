#! -*- coding: utf-8 -*-
from constance import config
import datetime
import uuid
import logging

from django.http import Http404
from django.http import HttpResponseRedirect

from django.shortcuts import redirect, render
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as _u
from django.contrib import messages
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, RedirectView, TemplateView, DetailView
from django.core.urlresolvers import reverse

from oscar.core.loading import get_class, get_model, get_classes
from oscar_webpay.gateway import get_webpay_client, confirm_transaction, acknowledge_transaction
from oscar_webpay.oscar_webpay_settings import oscar_webpay_settings as ow_settings
from oscar_webpay.models import WebPayTransaction

from oscar_webpay.exceptions import \
    AbortedTransactionByCardHolder, \
    MissingShippingMethodException, \
    MissingShippingAddressException, \
    AuthenticationError, \
    FailedTransaction, \
    TimeLimitExceeded, \
    U3Exception

import decimal

# Load views dynamically
PaymentDetailsView = get_class('checkout.views', 'PaymentDetailsView')
ThankYouView = get_class('checkout.views', 'ThankYouView')
CheckoutSessionMixin = get_class('checkout.session', 'CheckoutSessionMixin')
CheckoutSessionData = get_class('checkout.session', 'CheckoutSessionData')
Selector = get_class('partner.strategy', 'Selector')
OrderNumberGenerator = get_class('order.utils', 'OrderNumberGenerator')
SourceType = get_model('payment', 'SourceType')
Source = get_model('payment', 'Source')
Transaction = get_model('payment', 'Transaction')
Order = get_model('order', 'Order')
Basket = get_model('basket', 'Basket')

OrderCreator = get_class('order.utils', 'OrderCreator')

RedirectRequired, UnableToTakePayment, PaymentError \
    = get_classes('payment.exceptions', ['RedirectRequired',
                                         'UnableToTakePayment',
                                         'PaymentError'])

UnableToPlaceOrder = get_class('oscar.apps.order.exceptions', 'UnableToPlaceOrder')

try:
    Applicator = get_class('offer.applicator', 'Applicator')
except ModuleNotFoundError:
    # fallback for django-oscar<=1.1
    Applicator = get_class('offer.utils', 'Applicator')


logger = logging.getLogger('oscar_webpay')


class WebPayRedirectView(CheckoutSessionMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        # Init transaction, get url and token.

        basket = self.build_submission()['basket']
        order_number = OrderNumberGenerator().order_number(basket)

        total = basket.total_incl_tax

        # TODO: This is the correct way of doing things, remember to
        # TODO: implement a proper Shipping method with its corresponding method,
        # TODO: in order to calculate correctly the cost.

        # # Getting shipping charge.
        # if basket.is_shipping_required():
        #     # Only check for shipping details if required.
        #     shipping_addr = self.get_shipping_address(basket)
        #     if not shipping_addr:
        #         raise MissingShippingAddressException(shipping_addr)
        #
        #     shipping_method = self.get_shipping_method(
        #         basket, shipping_addr)
        #     if not shipping_method:
        #         raise MissingShippingMethodException(shipping_method)
        #     total += shipping_method.calculate(basket)


        # This is an ugly hack, very very ugly, this is
        # here only for villaflores purposes, do not push this
        # to the main branch.
        if basket.is_shipping_required():
            session_data = CheckoutSessionData(self.request)
            total += decimal.Decimal(session_data.get_shipping_cost())

        try:
            response = get_webpay_client(order_number, total)
        except Exception, unknown:
            messages.error(self.request, six.text_type(unknown))
            logger.error(six.text_type(unknown))
            return reverse("basket:summary")
        else:
            if response['token'] and response['url']:
                # Transaction successfully registered with WebPay.  Now freeze the
                # basket so it can't be edited while the customer is on the WebPay
                # site.
                logger.info("Basket #%s - redirecting to %s", basket.id, response['url'])
                self.request.session['webpay-payment-url'] = response['url']
                self.request.session['webpay-payment-token'] = response['token']
                self.request.session['webpay-payment-currency'] = basket.currency
                return reverse('webpay-form')
            else:
                # Something was wrong!!!  Call 911 !!!
                messages.error(self.request, _(u'WebPay is not available right now, or is presenting problems, please comback later.'))
                return reverse("basket:summary")

class WebPayRedirectForm(TemplateView):
    template_name = 'oscar_webpay/checkout/webpay_form.html'

    def get(self, request, *args, **kwargs):
        ctx = dict({
            'url': self.request.session['webpay-payment-url'],
            'token': self.request.session['webpay-payment-token'],
            'currency': self.request.session['webpay-payment-currency']
        })
        return render(request, self.template_name, ctx)


@method_decorator(csrf_exempt, name='dispatch')
class WebPayPaymentSuccessView(PaymentDetailsView):

    template_name_preview = 'oscar_webpay/checkout/webpay_preview.html'

    preview = True
    returning_from_webpay = True

    init_transaction_data = None

    def post(self, request, *args, **kwargs):
        if self.returning_from_webpay:
            self.request.session['webpay-token'] = request.POST['token_ws']
            try:
                self.init_transaction_data = confirm_transaction(self.request.session['webpay-token'])
            except TimeLimitExceeded as error:
                error_msg = _(u"Time limit exceeded")
                messages.error(self.request, msg)
                raise UnableToTakePayment(msg)
            except AbortedTransactionByCardHolder as error:
                msg = _(u"Transaction canceled by cardholder")
                messages.info(self.request, msg)
                return redirect('basket:summary')
            except FailedTransaction as error:
                msg = _(u"Failed transaction")
                messages.error(self.request, msg)
                raise UnableToTakePayment(msg)
            except U3Exception as error:
                msg = _(u"Authentication internal error")
                messages.error(self.request, msg)
                raise UnableToTakePayment(msg)
            except Exception as unknown_error:
                # TODO: write a good logic here to handle all the 328 possible exceptions
                messages.error(self.request, six.text_type(unknown_error))
                raise UnableToTakePayment(six.text_type(unknown_error))

            resp_code = self.init_transaction_data.detailOutput[0]['responseCode']

            if resp_code != 0:
                possible_errors = {
                    -1: _(u"Transaction rejected."),
                    -2: _(u"Transaction submitted again."),
                    -3: _(u"Error in transaction."),
                    -4: _(u"Transaction rejected."),
                    -5: _(u"Rejection by error of rate."),
                    -6: _(u"Exceeds monthly maximum quota."),
                    -7: _(u"Exceeds daily limit per transaction."),
                    -8: _(u"Unauthorized item.")
                }
                messages.error(request, possible_errors[resp_code])
                raise UnableToTakePayment(possible_errors[resp_code])

            return self.render_preview(
                request,
                auth_code=self.init_transaction_data.detailOutput[0].authorizationCode,
                txn_date=self.init_transaction_data.transactionDate,
                payment_type=self.init_transaction_data.detailOutput[0].paymentTypeCode,
                card_number=self.init_transaction_data.cardDetail.cardNumber,
                **kwargs
            )
        else:
            return super(WebPayPaymentSuccessView, self).post(request, *args, **kwargs)

    def build_submission(self, **kwargs):
        submission = super(WebPayPaymentSuccessView, self).build_submission(**kwargs)
        submission['order_kwargs'].update({
            'status': _(u'Settled')
        })
        return submission

    def handle_payment(self, order_number, total, **kwargs):
        """
        Complete payment with WebPay method to capture the money
        from the initial transaction.
        """
        logger.debug(_(u"Payment transaction with WebPay"))

        try:
            result = acknowledge_transaction(self.request.session['webpay-token'])
        except TimeLimitExceeded as error:
            error_msg = _(u"Time limit exceeded")
            messages.error(self.request, msg)
            raise UnableToTakePayment(msg)
        except AbortedTransactionByCardHolder as error:
            msg = _(u"Transaction canceled by cardholder")
            messages.info(self.request, msg)
            raise UnableToTakePayment(msg)
        except FailedTransaction as error:
            msg = _(u"Failed transaction")
            messages.error(self.request, msg)
            raise UnableToTakePayment(msg)
        except U3Exception as error:
            msg = _(u"Authentication internal error")
            messages.error(self.request, msg)
            raise UnableToTakePayment(msg)
        except Exception as unknown_error:
            # TODO: write a good loginc here to handle all the 328 possible exceptions
            messages.error(self.request, six.text_type(unknown_error))
            raise UnableToTakePayment(six.text_type(unknown_error))

        # Record payment source and event
        source_type, is_created = SourceType.objects.get_or_create(
            name='WebPay')

        basket = self.get_submitted_basket()

        # Assign strategy to basket instance
        if Selector:
            basket.strategy = Selector().strategy(self.request)

        # Re-apply any offers
        Applicator().apply(request=self.request, basket=basket)

        total_const = basket.total_incl_tax + decimal.Decimal(self.checkout_session.get_shipping_cost())

        source = Source(source_type=source_type,
                        currency=basket.currency,
                        amount_allocated=total_const,
                        amount_debited=total_const,
                        )

        self.add_payment_source(source)

        status = _(u'Settled')
        self.add_payment_event(status, total_const,
                               reference=order_number)

        source.create_deferred_transaction(
            Transaction.DEBIT,
            total_const,
            reference=str(uuid.uuid4()),
            status=status
        )


@method_decorator(csrf_exempt, name='dispatch')
class WebPayCancel(View):
    def post(self, request, *args, **kwargs):
        return redirect('basket:summary')


@method_decorator(csrf_exempt, name='dispatch')
class WebPayEndRedirect(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        if self.request.POST.get('TBK_TOKEN', False):
            msg = _(u"Transaction canceled by cardholder")
            messages.info(self.request, msg)
            return reverse("basket:summary")
        else:
            return reverse('webpay-txns')


@method_decorator(csrf_exempt, name='dispatch')
class WebPayThankYouView(ThankYouView):
    pass




@method_decorator(csrf_exempt, name='dispatch')
class WebPayFail(View):
    template_name = "checkout/payment_fail.html"

    def get_context_data(self, **kwargs):
        ctx = super(WebPayFail, self).get_context_data(**kwargs)
        return ctx
