# Generated by Django 5.1.3 on 2024-12-11 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0012_monthlysalary_exatra_sort_leave_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employeeinfo',
            name='joining_date',
        ),
        migrations.RemoveField(
            model_name='employeeinfo',
            name='position',
        ),
        migrations.AddField(
            model_name='employeeinfo',
            name='department',
            field=models.CharField(choices=[('HR', 'Human Resource'), ('administrative', 'Administrative'), ('software development', 'Software Development'), ('QA', 'Quality Assurance'), ('project management', 'Project Management'), ('Product Management', 'Product Management'), ('design', 'Design'), ('devOps', 'DevOps'), ('customer support', 'Customer Support'), ('marketing', 'Marketing'), ('IT', 'Information Technology')], default='IT', max_length=20),
        ),
    ]
