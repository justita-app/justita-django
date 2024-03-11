# Generated by Django 4.0.6 on 2024-03-09 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_lawyer_introduction_code'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lawyer',
            old_name='is_male',
            new_name='gender',
        ),
        migrations.AlterField(
            model_name='lawyer',
            name='introduction_code',
            field=models.CharField(blank=True, default='hc79iK', max_length=64, null=True),
        ),
    ]
