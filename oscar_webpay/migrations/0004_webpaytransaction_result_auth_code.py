# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-07-31 21:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oscar_webpay', '0003_remove_webpaytransaction_base_transaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='webpaytransaction',
            name='result_auth_code',
            field=models.IntegerField(choices=[(0, 'Approved transaction'), (-1, 'Transaction rejected.'), (-2, 'Transaction submitted again.'), (-3, 'Error in transaction.'), (-4, 'Transaction rejected.'), (-5, 'Rejection by error of rate.'), (-6, 'Exceeds monthly maximum quota.'), (-7, 'Exceeds daily limit per transaction.'), (-8, 'Unauthorized item.')], default=0, verbose_name='Result authentication code'),
            preserve_default=False,
        ),
    ]