from django.contrib import admin

from oscar_webpay import models

admin.site.register(models.WebPayTransaction)
