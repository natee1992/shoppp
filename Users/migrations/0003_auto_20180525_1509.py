# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-25 15:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0002_auto_20180525_1253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='walletdetails',
            name='wallet',
            field=models.ForeignKey(help_text='钱包', on_delete=django.db.models.deletion.CASCADE, to='Users.Wallet'),
        ),
    ]