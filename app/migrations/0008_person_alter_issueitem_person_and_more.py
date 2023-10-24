# Generated by Django 4.2.6 on 2023-10-19 07:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_alter_return_item_person'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person', models.CharField(max_length=20)),
            ],
        ),
        migrations.AlterField(
            model_name='issueitem',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.person'),
        ),
        migrations.AlterField(
            model_name='return_item',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.person'),
        ),
    ]
