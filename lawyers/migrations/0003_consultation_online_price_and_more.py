# Generated by Django 4.0.6 on 2024-03-10 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lawyers', '0002_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='consultation',
            name='online_price',
            field=models.IntegerField(default=100),
        ),
        migrations.AlterField(
            model_name='consultation',
            name='fifteen_min_price',
            field=models.IntegerField(default=30),
        ),
        migrations.AlterField(
            model_name='consultation',
            name='ten_min_price',
            field=models.IntegerField(default=15),
        ),
        migrations.AlterField(
            model_name='consultation',
            name='thirty_min_price',
            field=models.IntegerField(default=45),
        ),
    ]
