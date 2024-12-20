# Generated by Django 4.1.5 on 2023-02-03 04:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0006_alter_employeeinfo_joining_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeesalary',
            name='salary_of',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='salary_info', to='employee.employeeinfo'),
        ),
    ]
