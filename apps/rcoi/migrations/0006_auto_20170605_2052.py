# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-05 20:52
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rcoi', '0005_auto_20170605_1044'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscription',
            options={'ordering': ['employee']},
        ),
    ]
