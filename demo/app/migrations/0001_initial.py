# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-02-26 21:24
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import django_extensions.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('scim_id', models.CharField(blank=True, db_index=True, default=None, help_text='A unique identifier for a SCIM resource as defined by the service provider.', max_length=254, null=True, verbose_name='SCIM ID')),
                ('scim_external_id', models.CharField(blank=True, db_index=True, default=None, help_text='A string that is an identifier for the resource as defined by the provisioning client.', max_length=254, null=True, verbose_name='SCIM External ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('scim_username', models.CharField(blank=True, default=None, help_text="A service provider's unique identifier for the user", max_length=254, null=True, unique=True, verbose_name='SCIM Username')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('first_name', models.CharField(max_length=100, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=100, verbose_name='Last Name')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scim_id', models.CharField(blank=True, db_index=True, default=None, help_text='A unique identifier for a SCIM resource as defined by the service provider.', max_length=254, null=True, verbose_name='SCIM ID')),
                ('scim_external_id', models.CharField(blank=True, db_index=True, default=None, help_text='A string that is an identifier for the resource as defined by the provisioning client.', max_length=254, null=True, verbose_name='SCIM External ID')),
                ('scim_display_name', models.CharField(blank=True, db_index=True, default=None, help_text='A human-readable name for the Group.', max_length=254, null=True, verbose_name='SCIM Display Name')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Company')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GroupMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Group')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(through='app.GroupMembership', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Company'),
        ),
    ]
