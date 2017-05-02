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
CheckoutSessionMixin = get_class('checkout.session', 'CheckoutSessionMixin')
Selector = get_class('partner.strategy', 'Selector')

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


class WebPayRedirectView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse('webpay-details')


@method_decorator(csrf_exempt, name='dispatch')
class WebPayPaymentDetailsView(PaymentDetailsView):

    template_name_preview = 'oscar_webpay/checkout/webpay_preview.html'

    preview = True

    class JustSubmitting(object):
        """
        Context declaration to automaticaly set the attr that controls the
        behaviour of the methods according the configuration for the
        setting `ORDER_STATUS_BEFORE_PAYMENT`
        """
        def __init__(self, target):
            self.target = target

        def __enter__(self):
            self.target.submitting_just_order = True

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.target.submitting_just_order = False


    def __init__(self, *args, **kwargs):
        self.submitting_just_order = False
        super(PaymentDetailsView, self).__init__(*args, **kwargs)

    def submit_just_order(self, user, basket, shipping_address, shipping_method,  # noqa (too complex (10))
               shipping_charge, billing_address, order_total,
               payment_kwargs=None, order_kwargs=None):
        """
        This method is for handle the use case when `PLACE_ORDER_BEFORE_TAKE_PAYMENT` is True.
        We need to perform a serial of operations on the new order and later call the normal process
        for submission.

        This method sets the attribute `self.__submiting_just_order` to True in order to control
        the behaviour of the subsecuents calls to the others methods.

        When this method is completed `self.__submiting_just_order` is set to False again.

        """
        with self.JustSubmitting(self) as JSC:
            order_kwargs = {}
            # Do not care about actual payment process right now
            # just place the order.
            order_kwargs.update({
                'status': _(ow_settings.ORDER_STATUS_BEFORE_PAYMENT)
            })
            try:
                order_number = self.generate_order_number(basket)
                self.handle_order_placement(
                    order_number, user, basket, shipping_address, shipping_method,
                    shipping_charge, billing_address, order_total, **order_kwargs)
            except UnableToPlaceOrder as e:
                # It's possible that something will go wrong while trying to
                # actually place an order.  Not a good situation to be in as a
                # payment transaction may already have taken place, but needs
                # to be handled gracefully.
                msg = six.text_type(e)
                logger.error("Order #%s: unable to place order - %s",
                             order_number, msg, exc_info=True)
                self.restore_frozen_basket()
                return self.render_preview(
                    self.request, error=msg, **payment_kwargs)


    def get(self, request, *args, **kwargs):
        return self.render_preview(request, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(WebPayPaymentDetailsView, self).post(request, *args, **kwargs)

    def submit(self, user, basket, shipping_address, shipping_method,  # noqa (too complex (10))
               shipping_charge, billing_address, order_total,
               payment_kwargs=None, order_kwargs=None):
            return super(WebPayPaymentDetailsView, self).submit(
                user, basket, shipping_address,
                shipping_method, shipping_charge, billing_address, order_total,
                payment_kwargs, order_kwargs
            )

    def build_submission(self, **kwargs):
        submission = super(WebPayPaymentDetailsView, self).build_submission(**kwargs)
        submission['order_kwargs']['guest_email'] = self.checkout_session.get_guest_email()
        if self.request.user.is_authenticated():
            submission['order_kwargs']['user'] = self.request.user
        return submission

    def handle_place_order_submission(self, request):

        submission = self.build_submission()

        if ow_settings.PLACE_ORDER_BEFORE_TAKE_PAYMENT:
            # Submit just the order first ...
            self.submit_just_order(**submission)
        # and then call the normal submission process.
        return super(WebPayPaymentDetailsView, self).submit(**submission)


    def handle_payment(self, order_number, total, **kwargs):
        if not self.submitting_just_order:
            logger.debug(_(u"Initializing transaction with WebPay"))
            init_transaction_data = get_webpay_client(order_number, total)
            logger.debug(_(u"Redirecting to WebPay"))
            raise RedirectRequired(init_transaction_data['url'])
        else:
            # We don't  have any payment to handle while just submiting the order.
            pass

    def handle_order_placement(self, order_number, user, basket,
                               shipping_address, shipping_method,
                               shipping_charge, billing_address, order_total,
                               **kwargs):

        if self.submitting_just_order:

            # If order already set, there is no need to place it again.
            try:
                order = Order.objects.get(number=order_number)
            except Order.DoesNotExist:
                order = self.place_order(
                    order_number=order_number, user=user, basket=basket,
                    shipping_address=shipping_address, shipping_method=shipping_method,
                    shipping_charge=shipping_charge, order_total=order_total,
                    billing_address=billing_address, **kwargs)
                order.save()
                # When placing order before payment, there is no
                # reference. This can be updated when the payment has been
                # completed or some error happened.
                reference = '_'
                self.__add_payment_info("WebPay", order_total, reference, _(ow_settings.ORDER_STATUS_BEFORE_PAYMENT))
            else:
                # The order has been placed, don't do anything ...    please... it would be weird!
                pass
            return
        else:
            return super(WebPayPaymentDetailsView, self).handle_order_placement(
                order_number, user, basket,
                shipping_address, shipping_method,
                shipping_charge, billing_address, order_total,
                **kwargs
            )

    def __add_payment_info(self, source_type_name, total, reference, status):
        # Get source data.
        source_type = SourceType.objects.get_or_create(name=source_type_name)
        source = Source(
            source_type=source_type,
            amount_allocated=total.incl_tax,
            reference=reference)
        # Add payment info.
        self.add_payment_source(source)
        self.add_payment_event(status, total.incl_tax)


@method_decorator(csrf_exempt, name='dispatch')
class WebPayCancel(View):
    def post(self, request, *args, **kwargs):
        return redirect('basket:summary')

@method_decorator(csrf_exempt, name='dispatch')
class WebPayFail(View):
    template_name = "checkout/payment_fail.html"

    def get_context_data(self, **kwargs):
        ctx = super(WebPayFail, self).get_context_data(**kwargs)
        return ctx



