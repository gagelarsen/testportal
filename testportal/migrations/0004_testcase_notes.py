# Generated by Django 4.0.3 on 2022-06-19 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testportal', '0003_testcase_needs_review_testcase_under_construction'),
    ]

    operations = [
        migrations.AddField(
            model_name='testcase',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]