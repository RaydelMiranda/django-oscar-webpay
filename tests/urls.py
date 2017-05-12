from django.conf.urls import url, include

urlpatterns = [
    url(r'^test/', include('oscar_webpay.urls')),
]
