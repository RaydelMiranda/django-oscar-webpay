# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-07-31 22:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oscar_webpay', '0004_webpaytransaction_result_auth_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webpaytransaction',
            name='error_auth_code',
            field=models.CharField(choices=[(b'TSY', 'Successful authentication'), (b'TSN', 'Failed authentication'), (b'TO', 'Time limit exceeded'), (b'ABO', 'Transaction aborted by card holder'), (b'U3', 'Authentication internal error')], max_length=3, null=True, verbose_name='Error code'),
        ),
        migrations.AlterField(
            model_name='webpaytransaction',
            name='result_auth_code',
            field=models.IntegerField(blank=True, choices=[(0, 'Approved transaction'), (-1, 'Transaction rejected.'), (-2, 'Transaction submitted again.'), (-3, 'Error in transaction.'), (-4, 'Transaction rejected.'), (-5, 'Rejection by error of rate.'), (-6, 'Exceeds monthly maximum quota.'), (-7, 'Exceeds daily limit per transaction.'), (-8, 'Unauthorized item.')], null=True, verbose_name='Result authentication code'),
        ),
    ]