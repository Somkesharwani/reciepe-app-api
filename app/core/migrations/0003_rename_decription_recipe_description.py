# Generated by Django 3.2.16 on 2022-10-24 17:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_recipe'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='decription',
            new_name='description',
        ),
    ]
