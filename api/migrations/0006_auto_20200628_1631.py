# Generated by Django 3.0.6 on 2020-06-28 16:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20200625_1536'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('-created_on',)},
        ),
    ]