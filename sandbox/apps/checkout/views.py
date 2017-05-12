from django.shortcuts import redirect
from oscar.apps.checkout import views

class PaymentDetailsView(views.PaymentDetailsView):
    """
    An example view that shows how to integrate WebPay methods.
    """

    # WebPay does not require the submission of the cardholder data
    # this info will be gathered in the WebPay Form.
    preview = True

    def get_context_data(self, **kwargs):
        ctx = super(PaymentDetailsView, self).get_context_data(**kwargs)
        return ctx

    def get(self, request, *args, **kwargs):
        return redirect('webpay-redirect')