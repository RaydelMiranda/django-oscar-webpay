import os

from oscar import OSCAR_MAIN_TEMPLATE_DIR

BASE_DIR = os.path.dirname(__file__)

# Oscar-WebPay specific settings.
# ----------------------------------

WEBPAY_RETURN_IP_ADDRESS = '192.168.2.35'

WEBPAY_RETURN_PORT = 8001


WEBPAY_NORMAL = {
    'ACTIVE_ENVIRON': 'INTEGRATION',
    'ENVIRONMENTS': {
        'INTEGRATION': 'https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSWebpayService?wsdl',
        'CERTIFICATION': 'https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSWebpayService?wsdl',
        'PRODUCTION': 'https://webpay3g.transbank.cl/WSWebpayTransaction/cxf/WSWebpayService?wsdl',
    },
    'PRIVATE_KEY': os.path.join(BASE_DIR, 'integracion_normal/597020000541.key'),
    'PUBLIC_CERT': os.path.join(BASE_DIR, 'integracion_normal/597020000541.crt'),
    'WEBPAY_CERT': os.path.join(BASE_DIR, 'integracion_normal/tbk.pem'),
    'COMMERCE_CODE': '597020000541'
}

# Django Settings
# -------------------------------------


INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.staticfiles',
    'oscar_webpay',
    'compressor',
]

MIDDLEWARE_CLASSES = (
                         'django.middleware.common.CommonMiddleware',
                         'django.contrib.sessions.middleware.SessionMiddleware',
                         'django.middleware.csrf.CsrfViewMiddleware',
                         'django.contrib.auth.middleware.AuthenticationMiddleware',
                         'django.contrib.messages.middleware.MessageMiddleware',
                         'oscar.apps.basket.middleware.BasketMiddleware',
                     ),

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    # Oscar specific
    'oscar.apps.search.context_processors.search_form',
    'oscar.apps.promotions.context_processors.promotions',
    'oscar.apps.checkout.context_processors.checkout',
    'oscar.core.context_processors.metadata',
    'oscar.apps.customer.notifications.context_processors.notifications',
)


TEMPLATE_DIRS = (OSCAR_MAIN_TEMPLATE_DIR,),
ROOT_URLCONF = 'tests.urls',
COMPRESS_ENABLED = False,
STATIC_URL = '/',
STATIC_ROOT = '/static/',
