# Generated by Django 4.0.6 on 2024-03-11 14:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lawyers', '0017_lawyer_balance'),
        ('social', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='callcounseling',
            name='lawyer_model',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lawyers', to='lawyers.lawyer'),
        ),
    ]
