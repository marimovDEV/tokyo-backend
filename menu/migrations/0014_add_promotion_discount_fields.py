# Generated manually on 2025-01-27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0013_add_weight_order_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='promotion',
            name='discount_percentage',
            field=models.PositiveIntegerField(default=0, help_text='Discount percentage (0-100)'),
        ),
        migrations.AddField(
            model_name='promotion',
            name='discount_amount',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Discount amount in so\'m', max_digits=10),
        ),
        migrations.AddField(
            model_name='promotion',
            name='start_date',
            field=models.DateTimeField(blank=True, help_text='Promotion start date', null=True),
        ),
        migrations.AddField(
            model_name='promotion',
            name='end_date',
            field=models.DateTimeField(blank=True, help_text='Promotion end date', null=True),
        ),
    ]
