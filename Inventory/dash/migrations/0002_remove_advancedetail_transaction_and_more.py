# Generated by Django 5.2 on 2025-04-08 12:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='advancedetail',
            name='transaction',
        ),
        migrations.RemoveField(
            model_name='inventory',
            name='transaction',
        ),
        migrations.AddField(
            model_name='advancedetail',
            name='project',
            field=models.ForeignKey(default=0.0, on_delete=django.db.models.deletion.CASCADE, related_name='advance_details', to='dash.organization'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inventory',
            name='project',
            field=models.ForeignKey(default=0.0, on_delete=django.db.models.deletion.CASCADE, related_name='inventories', to='dash.organization'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='advance_total',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='project',
            name='buy_total',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='project',
            name='profit_total',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='project',
            name='sell_total',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.DeleteModel(
            name='Transaction',
        ),
    ]
