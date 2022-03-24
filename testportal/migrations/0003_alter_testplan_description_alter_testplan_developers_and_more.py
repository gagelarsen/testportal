# Generated by Django 4.0.3 on 2022-03-24 03:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testportal', '0002_testplan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testplan',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testplan',
            name='developers',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testplan',
            name='features_to_test',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testplan',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
