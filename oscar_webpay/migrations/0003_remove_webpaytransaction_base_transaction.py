# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-07-19 15:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oscar_webpay', '0002_auto_20170710_1156'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='webpaytransaction',
            name='base_transaction',
        ),
    ]