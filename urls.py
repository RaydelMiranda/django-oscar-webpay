from django.conf.urls import patterns, url
from oscar_webpay import views


urlpatterns = patterns(
    '',
    url(r'^webpay_payment/$', views.WebPayRedirect.as_view(), name='webpay-payment'),
    url(r'^webpay_detail/$', views.WebPayPaymentDetailsView.as_view(), name='webpay-details'),
    url(r'^webpay_fail/$', views.WebPayFail.as_view(), name='webpay-fail'),
    url(r'^webpay_cancel/$', views.WebPayCancel.as_view(), name='webpay-cancel'),
    url(r'^webpay_thanks/$', views.WebPayThankYouView.as_view(), name='webpay-tnx'),
    url(r'^webpay_thanks/$', views.WebPaySuccessView.as_view(), name='webpay-tnx'),
)
