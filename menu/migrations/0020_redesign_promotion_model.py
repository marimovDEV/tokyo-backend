# Generated manually for Promotion model redesign

from django.db import migrations, models
import django.db.models.deletion
from django.core.validators import MinValueValidator, MaxValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0019_fix_cascade_delete'),
    ]

    operations = [
        # Remove old fields
        migrations.RemoveField(
            model_name='promotion',
            name='category',
        ),
        migrations.RemoveField(
            model_name='promotion',
            name='linked_dish',
        ),
        
        # Add new fields
        migrations.AddField(
            model_name='promotion',
            name='discount_type',
            field=models.CharField(
                choices=[('percent', 'Foizda'), ('amount', 'Summada'), ('bonus', 'Bonus'), ('standalone', 'Mustaqil aksiya')],
                default='percent',
                help_text='Aksiya turi',
                max_length=15
            ),
        ),
        migrations.AddField(
            model_name='promotion',
            name='bonus_info',
            field=models.CharField(
                blank=True,
                help_text="Bonus ma'lumoti (masalan: 'Har 3 ta olganga 1 ta bepul')",
                max_length=300
            ),
        ),
        migrations.AddField(
            model_name='promotion',
            name='bonus_info_uz',
            field=models.CharField(
                blank=True,
                help_text="Bonus ma'lumoti (O'zbekcha)",
                max_length=300
            ),
        ),
        migrations.AddField(
            model_name='promotion',
            name='bonus_info_ru',
            field=models.CharField(
                blank=True,
                help_text="Bonus ma'lumoti (Ruscha)",
                max_length=300
            ),
        ),
        migrations.AddField(
            model_name='promotion',
            name='linked_product',
            field=models.ForeignKey(
                blank=True,
                help_text="Bog'langan mahsulot (bo'sh bo'lishi mumkin)",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='promotions',
                to='menu.menuitem'
            ),
        ),
        migrations.AddField(
            model_name='promotion',
            name='promotion_category',
            field=models.ForeignKey(
                blank=True,
                help_text='Aksiya kategoriyasi',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='menu.category'
            ),
        ),
        
        # Update existing fields
        migrations.AlterField(
            model_name='promotion',
            name='discount_percentage',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Chegirma foizi (0-100)',
                validators=[MinValueValidator(0), MaxValueValidator(100)]
            ),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='discount_amount',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='Chegirma summasi (so\'m)',
                max_digits=10
            ),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='start_date',
            field=models.DateTimeField(
                blank=True,
                help_text='Aksiya boshlanish vaqti',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='end_date',
            field=models.DateTimeField(
                blank=True,
                help_text='Aksiya tugash vaqti',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='image',
            field=models.ImageField(
                blank=True,
                help_text='Aksiya rasmi (bo\'lmasa, mahsulot rasmi ishlatiladi)',
                null=True,
                upload_to='promotions/'
            ),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='is_active',
            field=models.BooleanField(
                default=True,
                help_text='Aksiya faolmi?',
                verbose_name='Ko\'rinadi'
            ),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='price',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='Aksiya narxi (standalone aksiyalar uchun)',
                max_digits=10,
                validators=[MinValueValidator(0)]
            ),
        ),
    ]
