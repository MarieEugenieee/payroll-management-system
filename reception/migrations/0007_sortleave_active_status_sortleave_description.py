# Generated by Django 4.1.5 on 2023-02-05 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reception', '0006_remove_sortleave_active_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sortleave',
            name='active_status',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='sortleave',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]