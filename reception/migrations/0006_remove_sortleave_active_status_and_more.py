# Generated by Django 4.1.5 on 2023-02-05 13:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reception', '0005_sortleave_active_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sortleave',
            name='active_status',
        ),
        migrations.RemoveField(
            model_name='sortleave',
            name='description',
        ),
    ]
