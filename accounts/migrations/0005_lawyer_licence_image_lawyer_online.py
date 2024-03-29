# Generated by Django 4.0.6 on 2024-03-09 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_lawyer_options_remove_lawyer_is_lawyer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lawyer',
            name='licence_image',
            field=models.ImageField(blank=True, null=True, upload_to='licence_images'),
        ),
        migrations.AddField(
            model_name='lawyer',
            name='online',
            field=models.BooleanField(default=False),
        ),
    ]
