from django.contrib import admin
from .models import Product, ShoppingCart, OrderItem, Order, Like, Watch

admin.site.register(Product)
admin.site.register(ShoppingCart)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Like)
admin.site.register(Watch)


# Register your models here.
