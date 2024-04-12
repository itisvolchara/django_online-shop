from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import pytz


# Create your models here.
class ProductModel(models.Model):
    CATEGORIES = [
        ('FR', 'мебель'),
        ('TECH', 'техника'),
        ('DISH', 'посуда')
    ]

    CATEGORIES_DIR = dict(zip([i[1] for i in CATEGORIES], [i[0] for i in CATEGORIES]))

    name = models.CharField('Название', max_length=50)
    category = models.CharField('Категории', max_length=300, choices=CATEGORIES, default='FR')
    price = models.FloatField('Цена')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'


class ShoppingCartModel(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Shopping_cart'
        verbose_name_plural = 'Shopping_carts'


class OrderModel(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.FloatField('Стоимость заказа')
    date_time = models.DateTimeField('Дата покупки', blank=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def save(self, *args, **kwargs):
        timezone.activate(pytz.timezone('Europe/Moscow'))
        self.date_time = timezone.now()
        return super(OrderModel, self).save(*args, **kwargs)


class OrderItemModel(models.Model):
    order = models.ForeignKey(OrderModel, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'OrderItem'
        verbose_name_plural = 'OrderItems'


class LikeModel(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'


class WatchModel(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)

    date_time = models.DateTimeField('Дата просмотра', blank=True, null=True)

    class Meta:
        verbose_name = 'Watch'
        verbose_name_plural = 'Watches'

    def save(self, *args, **kwargs):
        timezone.activate(pytz.timezone('Europe/Moscow'))
        self.date_time = timezone.now()
        return super(WatchModel, self).save(*args, **kwargs)
