# Generated by Django 4.1.5 on 2023-02-17 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authority', '0010_leaveapplication'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaveapplication',
            name='declined_message',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='leaveapplication',
            name='declined_status',
            field=models.BooleanField(default=False),
        ),
    ]
