from django.db import migrations


GROUP_NAME = 'Category Managers'


def create_category_managers_group(apps, schema_editor):
    group_model = apps.get_model('auth', 'Group')
    group_model.objects.get_or_create(name=GROUP_NAME)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('testportal', '0010_alter_testcategory_category_and_more'),
    ]

    operations = [
        migrations.RunPython(create_category_managers_group, noop_reverse),
    ]
