# Generated by Django 4.2.6 on 2023-10-18 14:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_remove_custom_uom_id_alter_custom_uom_uom'),
    ]

    operations = [
        migrations.AlterField(
            model_name='return_item',
            name='person',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.issueitem'),
        ),
    ]
