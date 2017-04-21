#! -*- coding: utf-8 -*-
from constance import config

from django.http import Http404
from django.http import HttpResponseRedirect

from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, RedirectView, TemplateView, DetailView
from django.core.urlresolvers import reverse

from oscar.core.loading import get_class, get_model
# from oscar.apps.payment.exceptions import RedirectRequired
from oscar_webpay.gateway import get_webpay_client, confirm_transaction
from oscar.apps.payment.exceptions import RedirectRequired

import decimal

# Load views dynamically
PaymentDetailsView = get_class('checkout.views', 'PaymentDetailsView')
CheckoutSessionMixin = get_class('checkout.session', 'CheckoutSessionMixin')
Selector = get_class('partner.strategy', 'Selector')

SourceType = get_model('payment', 'SourceType')
Source = get_model('payment', 'Source')
Order = get_model('order', 'Order')



class WebPayRedirect(CheckoutSessionMixin, RedirectView):

    as_payment_method = False

    def get_redirect_url(self, *args, **kwargs):
        return reverse('webpay-details')


@method_decorator(csrf_exempt, name='dispatch')
class WebPayPaymentDetailsView(PaymentDetailsView):

    template_name = 'checkout/payment_details.html'
    # We use a specific template here because we inject the
    # WebPay url for the transaction to the form action attribute.
    template_name_preview = 'checkout/webpay_preview.html'

    preview = True

    def get_context_data(self, **kwargs):
        ctx = super(WebPayPaymentDetailsView, self).get_context_data(**kwargs)
        try:

            basket = self.build_submission()['basket']
            total = basket.total_incl_tax
            try:
                # Some customizations use shipping charge.
                total = basket.total_incl_tax + decimal.Decimal(ctx['shipping_charge'].incl_tax)
            except AttributeError:
                pass

            transaction = get_webpay_client(basket.pk, total)

            ctx['payment_url'] = transaction['url']
            ctx['token_ws'] = transaction['token']
            ctx['payment_method_webpay'] = True

            self.request.session['total'] = total
            self.request.session['order_number'] = basket.pk
            self.request.session['payment_url'] = ctx['payment_url']
            self.request.session['token'] = ctx['token_ws']

            pass
        except Exception as wpe:
            messages.error(self.request, wpe.message)
        else:
            return ctx

    def post(self, request, *args, **kwargs):
        error_msg = _(
            "A problem occurred communicating with WebPay "
            "- please try again later"
        )

        try:
            self.token = request.POST['token_ws']
        except KeyError:
            # Probably suspicious manipulation if we get here
            messages.error(self.request, error_msg)
            return HttpResponseRedirect(reverse('basket:summary'))

        submission = self.build_submission(**kwargs)
        return self.submit(**submission)

    def get(self, request):
        payment_method = self.checkout_session.payment_method()
        return self.render_preview(request, payment_method=payment_method)

    def build_submission(self, **kwargs):
        submission = super(WebPayPaymentDetailsView, self).build_submission()
        if hasattr(self, 'token'):
            # Execute this only when not in preview mode.
            submission['payment_kwargs']['token'] = self.token
        return submission

    def submit(self, **submission):
        return super(WebPayPaymentDetailsView, self).submit(**submission)

    def handle_payment(self, order_number, total, **kwargs):
        try:
            confirm_transaction(kwargs['token'])
        except Exception as wpe:
            messages.error(wpe)
            RedirectRequired(reverse('basket:summary'))
        source_type, is_created = SourceType.objects.get_or_create(
            name='WebPay')
        source = Source(
            source_type=source_type,
            currency=total.currency,
            amount_allocated=total.incl_tax,
        )
        self.add_payment_source(source)
        self.add_payment_event(_('Confirmed'), total.incl_tax)


class WebPaySuccessView(TemplateView):
    template_name = "checkout/payment_success.html"

    def get_context_data(self, **kwargs):
        ctx = super(WebPaySuccessView, self).get_context_data(**kwargs)
        order = ctx.get("order")
        lines = order.lines.all()
        products = []

        recomended = False
        for l in lines:
            product = l.product
            # products.append(l.product)
            if product.is_standalone or product.is_standalone:
                for p in product.recommended_products.all():
                    products.append(p)
            elif product.is_child:
                for p in product.parent.recommended_products.all():
                    products.append(p)

        if len(products) > 0:
            recomended = True

        basket = self.order.basket
        basket.strategy = Selector().strategy(self.request)

        ctx['recomended'] = recomended
        ctx['products'] = products
        ctx['lines'] = lines
        ctx['basket'] = basket
        # TODO: this is a dependence, refactor later.
        ctx['address'] = config.BUSINESS_ADDRESS

        return ctx


class WebPayCancel(View):
    def get(self, request, *args, **kwargs):
        return redirect('webpay-details')


class WebPayFail(View):
    template_name = "checkout/payment_fail.html"

    def get_context_data(self, **kwargs):
        ctx = super(WebPayFail, self).get_context_data(**kwargs)
        return ctx


@method_decorator(csrf_exempt, name='dispatch')
class WebPayThankYouView(View):
    """
    Displays the 'thank you' page which summarises the order just submitted.
    """
    template_name = 'checkout/thank_you.html'

    def post(self, request, *args, **kwargs):
        return render(request, 'checkout/thank_you.html', context={}, context_instance=RequestContext(request))

    def get(self, request, *args, **kwargs):
        pass