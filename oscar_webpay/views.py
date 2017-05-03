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
from oscar_webpay.gateway import get_webpay_client, confirm_transaction
from oscar_webpay.oscar_webpay_settings import oscar_webpay_settings as ow_settings

import decimal

# Load views dynamically
PaymentDetailsView = get_class('checkout.views', 'PaymentDetailsView')
ThankYouView = get_class('checkout.views', 'ThankYouView')
CheckoutSessionMixin = get_class('checkout.session', 'CheckoutSessionMixin')
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

logger = logging.getLogger('oscar_webpay')


class WebPayRedirectView(CheckoutSessionMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        # Init transaction, get url and token.

        basket = self.build_submission()['basket']
        order_number = OrderNumberGenerator().order_number(basket)
        total = basket.total_incl_tax + decimal.Decimal(self.request.session['shipping_charge'])

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
                # basket.freeze()
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

    def post(self, request, *args, **kwargs):
        if self.returning_from_webpay:
            self.request.session['webpay-token'] = request.POST['token_ws']
            return self.render_preview(request, **kwargs)
        else:
            return super(WebPayPaymentSuccessView, self).post(request, *args, **kwargs)

    def build_submission(self, **kwargs):
        submission = super(WebPayPaymentSuccessView, self).build_submission(**kwargs)
        submission['order_kwargs']['guest_email'] = self.checkout_session.get_guest_email()
        if self.request.user.is_authenticated():
            submission['order_kwargs']['user'] = self.request.user
        return submission

    def handle_payment(self, order_number, total, **kwargs):
        """
        Complete payment with WebPay method to capture the money 
        from the initial transaction.
        """
        logger.debug(_(u"Payment transaction with WebPay"))
        try:
            init_transaction_data = confirm_transaction(self.request.session['webpay-token'])
        except Exception as unknown_error:
            messages.error(self.request, six.text_type(unknown_error))
            raise UnableToTakePayment(six.text_type(unknown_error))

        resp_code = init_transaction_data.detailOutput[0]['responseCode']

        if resp_code != 0:

            possible_errors = {
                -1: _(u"Transaction rejected."),
                -2: _(u"Transaction submitted again."),
                -3: _(u"Error in transaction."),
                -4: _(u"Transaction rejected."),
                -5: _(u"TRejection by error of rate."),
                -6: _(u"Exceeds monthly maximum quota."),
                -7: _(u"Exceeds daily limit per transaction."),
                -8: _(u"Unauthorized item.")
            }
            messages.error(request, possible_errors[resp_code])
            raise UnableToTakePayment(possible_errors[resp_code])

        # Record payment source and event
        source_type, is_created = SourceType.objects.get_or_create(
            name='WebPay')

        basket = self.get_submitted_basket()

        source = Source(source_type=source_type,
                        currency=basket.currency,
                        amount_allocated=init_transaction_data.detailOutput[0]['amount']
        )
        self.add_payment_source(source)
        self.add_payment_event(_(u'Settled'), init_transaction_data.amount,
                               reference=init_transaction_data.buyOrder)


@method_decorator(csrf_exempt, name='dispatch')
class WebPayCancel(View):
    def post(self, request, *args, **kwargs):
        return redirect('basket:summary')


@method_decorator(csrf_exempt, name='dispatch')
class WebPayThankYouView(ThankYouView):
    pass

@method_decorator(csrf_exempt, name='dispatch')
class WebPayFail(View):
    template_name = "checkout/payment_fail.html"

    def get_context_data(self, **kwargs):
        ctx = super(WebPayFail, self).get_context_data(**kwargs)
        return ctx
