# Generated manually to fix CASCADE delete behavior

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0018_alter_promotion_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promotion',
            name='linked_dish',
            field=models.ForeignKey(
                blank=True, 
                help_text="Bog'langan taom", 
                null=True, 
                on_delete=models.CASCADE, 
                related_name='promotions', 
                to='menu.menuitem'
            ),
        ),
    ]
