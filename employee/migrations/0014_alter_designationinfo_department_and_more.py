# Generated by Django 4.1.5 on 2024-12-12 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0013_remove_employeeinfo_joining_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='designationinfo',
            name='department',
            field=models.CharField(choices=[('HR', 'Human Resource'), ('administrative', 'Administrative'), ('software development', 'Software Development'), ('QA', 'Quality Assurance'), ('project management', 'Project Management'), ('Product Management', 'Product Management'), ('design', 'Design'), ('devOps', 'DevOps'), ('customer support', 'Customer Support'), ('marketing', 'Marketing'), ('IT', 'Information Technology')], default='HR', max_length=20),
        ),
        migrations.AlterField(
            model_name='employeeinfo',
            name='department',
            field=models.CharField(choices=[('HR', 'Human Resource'), ('administrative', 'Administrative'), ('software development', 'Software Development'), ('QA', 'Quality Assurance'), ('project management', 'Project Management'), ('Product Management', 'Product Management'), ('design', 'Design'), ('devOps', 'DevOps'), ('customer support', 'Customer Support'), ('marketing', 'Marketing'), ('IT', 'Information Technology')], max_length=20),
        ),
    ]