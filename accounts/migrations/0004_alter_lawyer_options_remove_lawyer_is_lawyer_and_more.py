# Generated by Django 4.0.6 on 2024-03-09 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_lawyer_bio_alter_lawyer_introduction_code_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lawyer',
            options={'verbose_name': 'lawyer', 'verbose_name_plural': 'lawyers'},
        ),
        migrations.RemoveField(
            model_name='lawyer',
            name='is_lawyer',
        ),
        migrations.AddField(
            model_name='user',
            name='is_lawyer',
            field=models.BooleanField(default=False),
        ),
    ]