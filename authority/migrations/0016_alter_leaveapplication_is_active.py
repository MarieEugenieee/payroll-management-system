# Generated by Django 4.1.5 on 2023-02-17 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authority', '0015_leaveapplication_employee_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaveapplication',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]