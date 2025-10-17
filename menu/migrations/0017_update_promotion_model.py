# Generated manually
from django.db import migrations, models
from django.core.validators import MinValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0016_merge_20251017_0948'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promotion',
            name='active',
        ),
        migrations.RemoveField(
            model_name='promotion',
            name='link',
        ),
        migrations.AddField(
            model_name='promotion',
            name='price',
            field=models.DecimalField(decimal_places=2, help_text='Aksiya narxi', max_digits=10, validators=[MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='promotion',
            name='ingredients',
            field=models.JSONField(blank=True, default=list, help_text='Tarkibi'),
        ),
        migrations.AddField(
            model_name='promotion',
            name='ingredients_uz',
            field=models.JSONField(blank=True, default=list, help_text='Tarkibi (O\'zbekcha)'),
        ),
        migrations.AddField(
            model_name='promotion',
            name='ingredients_ru',
            field=models.JSONField(blank=True, default=list, help_text='Tarkibi (Ruscha)'),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name="Ko'rinadi"),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='category',
            field=models.ForeignKey(blank=True, help_text='Aksiya kategoriyasi', null=True, on_delete=models.deletion.CASCADE, to='menu.category'),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='linked_dish',
            field=models.ForeignKey(blank=True, help_text='Bog\'langan taom', null=True, on_delete=models.deletion.SET_NULL, related_name='promotions', to='menu.menuitem'),
        ),
    ]
