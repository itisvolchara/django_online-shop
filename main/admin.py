from django.contrib import admin
from .models import Product, ShoppingCart, OrderItem, Order, Like

admin.site.register(Product)
admin.site.register(ShoppingCart)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Like)


# Register your models here.
