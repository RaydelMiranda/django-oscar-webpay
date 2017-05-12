import os

from oscar.defaults import *
from oscar import OSCAR_MAIN_TEMPLATE_DIR, get_core_apps

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

SECRET_KEY = 'FALSE-KEY-000'

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
] + get_core_apps()

MIDDLEWARE_CLASSES = (
     'django.middleware.common.CommonMiddleware',
     'django.contrib.sessions.middleware.SessionMiddleware',
     'django.middleware.csrf.CsrfViewMiddleware',
     'django.contrib.auth.middleware.AuthenticationMiddleware',
     'django.contrib.messages.middleware.MessageMiddleware',
     'oscar.apps.basket.middleware.BasketMiddleware'
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'oscar_webpay/templates'),
            OSCAR_MAIN_TEMPLATE_DIR
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.core.context_processors.request',

                'oscar.apps.search.context_processors.search_form',
                'oscar.apps.promotions.context_processors.promotions',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.apps.customer.notifications.context_processors.notifications',
                'oscar.core.context_processors.metadata',

            ],
            'loaders': [
                'app_namespace.Loader',
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    }
]

ROOT_URLCONF = 'tests.urls'
COMPRESS_ENABLED = False
STATIC_ROOT = '/'
STATIC_URL = '/static/'
COMPRESS_URL = 'compress/'

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

