# Generated by Django 4.0.3 on 2022-06-02 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testportal', '0002_testresult_bug_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='testcase',
            name='needs_review',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='testcase',
            name='under_construction',
            field=models.BooleanField(default=False),
        ),
    ]
