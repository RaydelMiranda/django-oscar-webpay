import os
from django.conf import settings

OSCAR_WEBPAY_TEMPLATES_DIR = os.path.join(
    os.path.dirname(__file__), 'templates'
)


settings.LOCALE_PATHS = settings.LOCALE_PATHS + (os.path.join(os.path.dirname(__file__), 'locale/'), )
