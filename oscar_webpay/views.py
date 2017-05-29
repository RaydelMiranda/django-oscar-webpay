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

Applicator = get_class('offer.applicator', 'Applicator')


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
            response = get_webpay_client(
                order_number, total, 'webpay-success', 'webpay-end-redirect'
            )
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
                return reverse("webpay-fail")


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

    def post(self, request, *args, **kwargs):
        if self.returning_from_webpay:
            self.request.session['webpay-token'] = request.POST['token_ws']
            return self.render_preview(request, **kwargs)
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
        generic_error_message = _(u"Something went wrong, plese try again later.")

        try:
            confirmed_transaction = confirm_transaction(self.request.session['webpay-token'])
            result = acknowledge_transaction(self.request.session['webpay-token'])
        except TimeLimitExceeded as error:
            error_msg = _(u"Time limit exceeded")
            messages.error(self.request, error_msg)
            raise PaymentError(error_msg)
        except AbortedTransactionByCardHolder as error:
            error_msg = _(u"Transaction canceled by cardholder")
            messages.info(self.request, error_msg)
            raise PaymentError(error_msg)
        except FailedTransaction as error:
            error_msg = _(u"Failed transaction")
            messages.error(self.request, error_msg)
            raise PaymentError(error_msg)
        except U3Exception as error:
            error_msg = _(u"Authentication internal error")
            messages.error(self.request, error_msg)
            raise PaymentError(error_msg)
        except TimeLimitExceeded as error:
            error_msg = _(u"Time limit exceeded")
            messages.error(self.request, error_msg)
            raise PaymentError(error_msg)
        except AbortedTransactionByCardHolder as error:
            error_msg = _(u"Transaction canceled by cardholder")
            messages.info(self.request, error_msg)
            raise PaymentError(error_msg)
        except FailedTransaction as error:
            error_msg = _(u"Failed transaction")
            messages.error(self.request, error_msg)
            raise PaymentError(error_msg)
        except U3Exception as error:
            error_msg = _(u"Authentication internal error")
            messages.error(self.request, error_msg)
            raise PaymentError(error_msg)
        except Exception as unknown_error:
            # TODO: write a good logic here to handle all the 328 possible exceptions
            logger.error(six.text_type(unknown_error))
            messages.error(self.request, generic_error_message)
            raise PaymentError(unknown_error)

        resp_code = confirmed_transaction.detailOutput[0]['responseCode']

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
            messages.error(self.request, possible_errors[resp_code])
            raise PaymentError(possible_errors[resp_code])

        # Record payment source and event
        source_type, is_created = SourceType.objects.get_or_create(
            code="webpay-transbank", name=u"Tarjeta de crédito o redcompra (Transbank / Webpay plus)")

        basket = self.get_submitted_basket()

        # Assign strategy to basket instance
        if Selector:
            basket.strategy = Selector().strategy(self.request)

        # Re-apply any offers
        Applicator().apply(request=self.request, basket=basket)

        # TODO: Hmmmmmmm ...
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

        # Save transaction details in order to make them available min the thanks view
        transaction_details = dict({
            # TypeTransactionResultOutput.cardDetail
            # -------------------------------------------
            'webpay_buy_order': confirmed_transaction.buyOrder,
            'webpay_accounting_date': confirmed_transaction.accountingDate,
            'webpay_transaction_date': confirmed_transaction.transactionDate,
            'webpay_VCI': confirmed_transaction.VCI,
            'webpay_url_redirection': confirmed_transaction.urlRedirection,
            # TypeTransactionResultOutput.detailOuput
            # -------------------------------------------
            'webpay_authorization_code': confirmed_transaction.detailOutput[0].authorizationCode,
            'webpay_amount': confirmed_transaction.detailOutput[0].amount,
            'webpay_commerce_code': confirmed_transaction.detailOutput[0].commerceCode,
            'webpay_buyOrder': confirmed_transaction.detailOutput[0].buyOrder,
            'webpay_shares_number': confirmed_transaction.detailOutput[0].sharesNumber,
            'webpay_response_code': confirmed_transaction.detailOutput[0].responseCode,
            'webpay_payment_type_code': confirmed_transaction.detailOutput[0].paymentTypeCode,
            # TypeTransactionResultOutput.cardDetails
            # -------------------------------------------
            'webpay_card_number': confirmed_transaction.cardDetail.cardNumber,
            # (Optional) Credit card expiration date of Cardholder. Format YYMM
            # Only for Transbank authorized merchants.
            'webpay_card_expiration_date': confirmed_transaction.cardDetail.cardExpirationDate if \
            hasattr(confirmed_transaction.cardDetail, 'cardExpirationDate') else None
        })
        self.save_transaction_details(**transaction_details)

        self.request.session['payment_url'] = confirmed_transaction.urlRedirection
        raise RedirectRequired(reverse('webpay-form'))

    def save_transaction_details(self, **kwargs):
        """
        This view is for saving the transaction details to the section data in order to
        make then available to the thanks view.

        :param request:  The request of the current view.
        :param kwargs:   All the key value pairs to save in the session.
        :return: None
        """
        self.request.session.update(kwargs)

    def get_success_url(self):
        return reverse('webpay-txns')


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
            return reverse("webpay-fail", args=(self.request.session['order_number'], msg))
        else:
            return reverse('webpay-txns')


@method_decorator(csrf_exempt, name='dispatch')
class WebPayThankYouView(ThankYouView):
    template_name = 'oscar_webpay/checkout/webpay_thank_you.html'

    def get_context_data(self, **kwargs):
        ctx = super(WebPayThankYouView, self).get_context_data(**kwargs)


        ctx.update({
            # TypeTransactionResultOutput.cardDetail
            # -------------------------------------------
            'webpay_buy_order': self.request.session['webpay_buy_order'],
            'webpay_accounting_date': self.request.session['webpay_accounting_date'],
            'webpay_transaction_date': self.request.session['webpay_transaction_date'],
            'webpay_VCI': self.request.session['webpay_VCI'],
            'webpay_url_redirection': self.request.session['webpay_url_redirection'],
            # TypeTransactionResultOutput.detailOuput
            # -------------------------------------------
            'webpay_authorization_code': self.request.session['webpay_authorization_code'],
            'webpay_amount': self.request.session['webpay_amount'],
            'webpay_commerce_code': self.request.session['webpay_commerce_code'],
            'webpay_buyOrder': self.request.session['webpay_buyOrder'],
            'webpay_shares_number': int(self.request.session['webpay_shares_number']),
            'webpay_shares_amount': float(self.request.session['webpay_shares_amount']),
            'webpay_response_code': self.request.session['webpay_response_code'],
            'webpay_payment_type_code': self.request.session['webpay_payment_type_code'],
            # TypeTransactionResultOutput.cardDetails
            # -------------------------------------------
            'webpay_card_number': self.request.session['webpay_card_number'],
            # Card
            'webpay_card_expiration_date': self.request.session['webpay_card_expiration_date']
        })

        if (int(self.request.session['webpay_shares_number']) > 0):
            shares_amount = self.request.session['webpay_shares_amount']
            shares_number = self.request.session['webpay_shares_number']
            ctx.update({'cuotes': [float(shares_amount)] * int(shares_number)})

        return ctx


@method_decorator(csrf_exempt, name='dispatch')
class WebPayFail(View):
    template_name = "checkout/payment_failed.html"

    def get_context_data(self, **kwargs):
        ctx = super(WebPayFail, self).get_context_data(**kwargs)
        return ctx
