# Generated by Django 4.0.6 on 2024-03-09 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_rename_is_male_lawyer_gender_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lawyer',
            name='gender',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='lawyer',
            name='introduction_code',
            field=models.CharField(default=None, max_length=64),
        ),
    ]
