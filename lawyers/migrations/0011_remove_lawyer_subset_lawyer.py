# Generated by Django 4.0.6 on 2024-03-10 20:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lawyers', '0010_alter_lawyer_introduction_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lawyer',
            name='subset_lawyer',
        ),
    ]
