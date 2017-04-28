#! -*- coding: utf-8 -*-
from constance import config
import datetime

from django.http import Http404
from django.http import HttpResponseRedirect

from django.shortcuts import redirect, render
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.contrib import messages
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, RedirectView, TemplateView, DetailView
from django.core.urlresolvers import reverse

from oscar.core.loading import get_class, get_model, get_classes
from oscar_webpay.gateway import get_webpay_client, confirm_transaction

import decimal

# Load views dynamically
PaymentDetailsView = get_class('checkout.views', 'PaymentDetailsView')
CheckoutSessionMixin = get_class('checkout.session', 'CheckoutSessionMixin')
Selector = get_class('partner.strategy', 'Selector')

SourceType = get_model('payment', 'SourceType')
Source = get_model('payment', 'Source')
Order = get_model('order', 'Order')
Basket = get_model('basket', 'Basket')

OrderCreator = get_class('order.utils', 'OrderCreator')

RedirectRequired, UnableToTakePayment, PaymentError \
    = get_classes('payment.exceptions', ['RedirectRequired',
                                         'UnableToTakePayment',
                                         'PaymentError'])


class WebPayRedirect(CheckoutSessionMixin, RedirectView):
    as_payment_method = False

    def get_redirect_url(self, *args, **kwargs):
        return reverse('webpay-details')


class WebPayForm(TemplateView):
    template_name = 'checkout/webpay_form.html'

    def get_context_data(self, **kwargs):
        ctx = super(WebPayForm, self).get_context_data(**kwargs)
        ctx.update({
            'payment_url': self.request.session['payment_url'],
            'token_ws': self.request.session['token']
        })
        return ctx


@method_decorator(csrf_exempt, name='dispatch')
class WebPayPaymentDetailsView(PaymentDetailsView):
    template_name = 'checkout/payment_details.html'
    template_name_preview = 'checkout/webpay_preview.html'

    preview = True
    payment_mode = False

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

            ctx['payment_url'] = reverse('webpay-details')
            ctx['token_ws'] = transaction['token']
            ctx['payment_method_webpay'] = True

            self.request.session['total'] = total
            self.request.session['order_number'] = basket.pk
            self.request.session['payment_url'] = transaction['url']
            self.request.session['token'] = ctx['token_ws']
            self.request.session['shipping_charge'] = ctx['shipping_charge'].incl_tax

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

        if not self.payment_mode:
            basket = kwargs.get('basket', self.request.basket)
            shipping_address = self.get_shipping_address(basket)
            shipping_method = self.get_shipping_method(
                basket, shipping_address)
            billing_address = self.get_billing_address(shipping_address)


            if not shipping_method:
                total = shipping_charge = None
            else:
                shipping_charge = shipping_method.calculate(basket)
                total = self.get_order_totals(
                    basket, shipping_charge=shipping_charge)
            order_number = self.generate_order_number(basket)

            try:
                Order.objects.get(number=order_number)
            except Order.DoesNotExist:
                self.place_order(
                    order_number=order_number, user=request.user, basket=basket,
                    shipping_address=shipping_address, shipping_method=shipping_method,
                    shipping_charge=shipping_charge, order_total=total,
                    billing_address=billing_address, **(submission['order_kwargs'])
                )

            return redirect('webpay-form')
        return self.submit(**submission)

    def get(self, request):
        payment_method = self.checkout_session.payment_method()
        return self.render_preview(request, payment_method=payment_method)

    def build_submission(self, **kwargs):
        submission = super(WebPayPaymentDetailsView, self).build_submission()
        if hasattr(self, 'token'):
            # Execute this only when not in preview mode.
            submission['payment_kwargs']['token'] = self.token
            # Set the initial state of payment to In process':
            # TODO: Make correct translation here.
            submission['order_kwargs']['status'] = _(u"Pendiente confirmación")
            submission['order_kwargs']['client_desired_dispatch_date'] = dispath_date = datetime.datetime.strptime(
                self.checkout_session.get_shipping_date(), "%d/%m/%Y"
            ).date()
            submission["order_kwargs"]["client_desired_dispatch_time"] = self.checkout_session.get_shipping_time()
        return submission

    def submit(self, **submission):
        return super(WebPayPaymentDetailsView, self).submit(**submission)

    def handle_order_placement(self, order_number, user, basket, shipping_address, shipping_method,
                               shipping_charge, billing_address, order_total, **order_kwargs):

        # This is really a crap!!  But I'm working right now on top
        # of a legacy work and the time line is short. I swear I'll be
        # comback to this code latter!!!!
        order = Order.objects.get(number=order_number)
        self.save_payment_details(order)
        if self.order_status_value == 1:
            # Some thing was wrong with payment.
            return redirect("basket:summary")
        else:
            return self.handle_successful_order(order)


    def handle_payment(self, order_number, total, **kwargs):
        try:
            result = confirm_transaction(kwargs['token'])
        except Exception as wpe:
            raise PaymentError(six.text_type(wpe))
        else:
            source_type, is_created = SourceType.objects.get_or_create(name='WebPay')
            source = Source(
                source_type=source_type,
                currency=total.currency,
                amount_allocated=total.incl_tax,
            )
            respCode = result.detailOutput[0]['responseCode']
            if (result['VCI'] == 'TSY' or result['VCI'] == '') and respCode == 0:
                self.add_payment_source(source)
                self.add_payment_event(_(u'Pago confirmado'), total.incl_tax)
                self.order_status = _(u'Pago confirmado')
                order = Order.objects.get(number=order_number)
                order.status = _(u'Pago confirmado')
                order.save()
                self.order_status_value = 0
            else:
                self.add_payment_source(source)
                self.add_payment_event(_(u'Pendiente confirmación'), total.incl_tax)
                self.order_status = _(u'Pendiente confirmación')
                self.order_status_value = 1

            return None

@method_decorator(csrf_exempt, name='dispatch')
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
