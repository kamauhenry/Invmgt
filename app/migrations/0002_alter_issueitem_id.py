# Generated by Django 4.2.6 on 2023-10-11 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issueitem',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
