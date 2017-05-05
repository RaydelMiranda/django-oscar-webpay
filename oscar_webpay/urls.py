from django.conf.urls import patterns, url
from oscar_webpay import views


urlpatterns = patterns(
    '',
    url(r'^webpay_redirect/(?P<return_url_name>\w|\-)+/(?P<final_url_name>\w|\-)+/$', views.WebPayRedirectView.as_view(),
        name='webpay-redirect'),
    url(r'^webpay_form/$', views.WebPayRedirectForm.as_view(), name='webpay-form'),
    url(r'^webpay_success/$', views.WebPayPaymentSuccessView.as_view(), name='webpay-success'),
    url(r'^webpay_place_order/$', views.WebPayPaymentSuccessView.as_view(returning_from_webpay=False),
        name='webpay-place-order'),
    url(r'^webpay_thanks/$', views.WebPayThankYouView.as_view(), name='webpay-txns'),
    url(r'^webpay_fail/$', views.WebPayFail.as_view(), name='webpay-fail'),
    url(r'^webpay_cancel/$', views.WebPayCancel.as_view(), name='webpay-cancel'),
    url(r'^webpay_end_redirect/$', views.WebPayEndRedirect.as_view(), name='webpay-end-redirect'),
)
