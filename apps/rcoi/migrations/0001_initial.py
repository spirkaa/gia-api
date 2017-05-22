# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-22 13:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=50, verbose_name='Название')),
                ('url', models.URLField(verbose_name='Ссылка на источник данных')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Date',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('date', models.DateField(db_index=True, unique=True, verbose_name='Дата экзамена')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(db_index=True, max_length=150, verbose_name='ФИО')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('date', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exams', to='rcoi.Date')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exams', to='rcoi.Employee')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('level', models.CharField(db_index=True, max_length=3, unique=True, verbose_name='Уровень экзамена')),
            ],
            options={
                'ordering': ['level'],
            },
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(db_index=True, max_length=500, unique=True, verbose_name='Место работы')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('code', models.CharField(db_index=True, max_length=5, verbose_name='Код ППЭ')),
                ('name', models.CharField(db_index=True, max_length=500, verbose_name='Наименование ППЭ')),
                ('addr', models.CharField(db_index=True, max_length=255, verbose_name='Адрес ППЭ')),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(db_index=True, max_length=100, unique=True, verbose_name='Должность в ППЭ')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Territory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('code', models.CharField(db_index=True, max_length=5, unique=True, verbose_name='Код АТЕ')),
                ('name', models.CharField(db_index=True, max_length=150, verbose_name='Наименование АТЕ')),
            ],
            options={
                'verbose_name_plural': 'Territories',
                'ordering': ['code'],
            },
        ),
        migrations.AddField(
            model_name='place',
            name='ate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='places', to='rcoi.Territory'),
        ),
        migrations.AddField(
            model_name='exam',
            name='level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exams', to='rcoi.Level'),
        ),
        migrations.AddField(
            model_name='exam',
            name='place',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exams', to='rcoi.Place'),
        ),
        migrations.AddField(
            model_name='exam',
            name='position',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exams', to='rcoi.Position'),
        ),
        migrations.AddField(
            model_name='employee',
            name='org',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='rcoi.Organisation'),
        ),
        migrations.AlterUniqueTogether(
            name='place',
            unique_together=set([('code', 'name', 'addr', 'ate')]),
        ),
        migrations.AlterUniqueTogether(
            name='exam',
            unique_together=set([('date', 'level', 'place', 'employee')]),
        ),
        migrations.AlterUniqueTogether(
            name='employee',
            unique_together=set([('name', 'org')]),
        ),
    ]
