# Generated by Django 5.0.3 on 2024-03-21 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_order_shoppingcart_delete_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_id',
            field=models.IntegerField(default=0, verbose_name='Номер заказа'),
        ),
    ]
