# Generated by Django 5.2 on 2025-04-08 13:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0003_remove_advancedetail_datetime_advancedetail_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advancedetail',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='advance_details', to='dash.project'),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventories', to='dash.project'),
        ),
    ]
