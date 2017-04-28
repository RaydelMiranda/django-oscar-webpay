from django.conf.urls import patterns, url
from oscar_webpay import views


urlpatterns = patterns(
    '',
    url(r'^webpay_payment/$', views.WebPayRedirect.as_view(), name='webpay-payment'),
    url(r'^webpay_detail/$', views.WebPayPaymentDetailsView.as_view(), name='webpay-details'),
    # We use a specific template here because we inject the
    # WebPay url for the transaction to the form action attribute.
    url(r'^webpay_detail/returns/$', views.WebPayPaymentDetailsView.as_view(
        payment_mode=True
    ), name='webpay-details-returns'),
    url(r'^webpay_fail/$', views.WebPayFail.as_view(), name='webpay-fail'),
    url(r'^webpay_form/$', views.WebPayForm.as_view(), name='webpay-form'),
    url(r'^webpay_cancel/$', views.WebPayCancel.as_view(), name='webpay-cancel'),
    url(r'^webpay_thanks/$', views.WebPayThankYouView.as_view(), name='webpay-tnx'),
    url(r'^webpay_thanks/$', views.WebPaySuccessView.as_view(), name='webpay-success'),
)
