from django.conf.urls import patterns, url
from oscar_webpay import views


urlpatterns = patterns(
    '',
    url(r'^webpay_redirect/$', views.WebPayRedirectView.as_view(), name='webpay-redirect'),
    url(r'^webpay_detail/$', views.WebPayPaymentDetailsView.as_view(), name='webpay-details'),
    url(r'^webpay_fail/$', views.WebPayFail.as_view(), name='webpay-fail'),
    url(r'^webpay_cancel/$', views.WebPayCancel.as_view(), name='webpay-cancel'),
)
