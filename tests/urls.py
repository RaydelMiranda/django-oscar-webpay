from django.conf.urls import url, include
from oscar.app import application

urlpatterns = [
    url(r'^test/', include('oscar_webpay.urls')),
    # Oscar urls.
    url(r'', include(application.urls))
]
