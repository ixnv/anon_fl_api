# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-11 18:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20161211_1638'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderchat',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
