# Generated by Django 4.2.6 on 2023-10-19 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_person_alter_issueitem_person_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sqlserverconn',
            name='Item',
            field=models.CharField(db_column='Item', db_index=True, max_length=30),
        ),
    ]
