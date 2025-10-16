# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0012_alter_category_options_alter_menuitem_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='order',
            field=models.PositiveIntegerField(default=0, help_text='Display order'),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='weight',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Weight in grams', max_digits=8, null=True, validators=[models.fields.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['order', 'name'], 'verbose_name': 'Kategoriya', 'verbose_name_plural': 'Kategoriyalar'},
        ),
    ]
