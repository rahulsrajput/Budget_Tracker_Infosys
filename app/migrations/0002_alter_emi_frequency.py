# Generated by Django 5.1.3 on 2024-11-24 04:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emi',
            name='frequency',
            field=models.CharField(choices=[('Monthly', 'Monthly'), ('Weekly', 'Weekly'), ('Quarterly', 'Quarterly')], default='Monthly', max_length=20),
        ),
    ]
