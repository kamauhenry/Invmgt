# Generated by Django 4.2.6 on 2023-10-24 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_alter_sqlserverconn_unit_of_measurement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sqlserverconn',
            name='Units',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
        ),
    ]