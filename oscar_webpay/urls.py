"""
Copyright (2017) Raydel Miranda 

This file is part of Django Oscar WebPay.

    Django Oscar WebPay is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Django Oscar WebPay is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Django Oscar WebPay.  If not, see <http://www.gnu.org/licenses/>.
"""

from django.conf.urls import url
from oscar_webpay import views


urlpatterns = [
    url(r'^webpay_redirect/(?P<return_url_name>(\w|[/:.-]|\d)+)/(?P<final_url_name>(\w|[/:.-]|\d)+)/$',
        views.WebPayRedirectView.as_view(),
        name='webpay-redirect'),
    url(r'^webpay_form/(?P<url>(\w|[/:.-]|\d)+)/(?P<token>(\w|-|\d)+)/$', views.WebPayRedirectForm.as_view(),
        name='webpay-form'),
    url(r'^webpay_success/$', views.WebPayPaymentSuccessView.as_view(),
        name='webpay-success'),
    url(r'^webpay_place_order/$', views.WebPayPaymentSuccessView.as_view(returning_from_webpay=False),
        name='webpay-place-order'),
    url(r'^webpay_thanks/$', views.WebPayThankYouView.as_view(),
        name='webpay-txns'),
    url(r'^webpay_fail/$', views.WebPayFail.as_view(),
        name='webpay-fail'),
    url(r'^webpay_cancel/$', views.WebPayCancel.as_view(),
        name='webpay-cancel'),
    url(r'^webpay_end_redirect/$', views.WebPayEndRedirect.as_view(),
        name='webpay-end-redirect'),
]
