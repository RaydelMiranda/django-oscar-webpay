# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-08-10 20:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oscar_webpay', '0005_auto_20170731_1820'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webpaytransaction',
            name='error_auth_code',
            field=models.CharField(choices=[(b'TSY', 'Successful authentication'), (b'TSN', 'Failed authentication'), (b'TO', 'Time limit exceeded'), (b'ABO', 'Transaction aborted by card holder'), (b'U3', 'Authentication internal error')], max_length=3, null=True, verbose_name='Result authentication code'),
        ),
    ]
