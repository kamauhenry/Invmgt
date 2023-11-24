# Generated by Django 4.2.6 on 2023-11-23 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_delete_labour121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupeditems',
            name='total',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='groupeditems',
            name='total_units',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='groupeditems',
            name='units_available',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='groupeditems',
            name='used_units',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='issueitem',
            name='units_issued',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='issueitem',
            name='units_returned',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='issueitem',
            name='units_used',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='labour',
            name='labourer_cost',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='labour',
            name='sub_total',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='sqlserverconn',
            name='Subtotal',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='sqlserverconn',
            name='Unit_cost',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='sqlserverconn',
            name='Units',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=15),
        ),
    ]