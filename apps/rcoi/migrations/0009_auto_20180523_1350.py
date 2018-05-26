# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-05-23 13:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rcoi', '0008_auto_20170622_2242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='ate',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='places', to='rcoi.Territory'),
        ),
        migrations.AlterUniqueTogether(
            name='place',
            unique_together=set([('code', 'name', 'addr')]),
        ),
    ]
