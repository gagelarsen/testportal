# Generated by Django 4.0.3 on 2022-05-06 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testportal', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='testresult',
            name='bug_id',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
