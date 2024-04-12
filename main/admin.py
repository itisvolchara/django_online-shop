from django.contrib import admin
from .models import ProductModel, ShoppingCartModel, OrderItemModel, OrderModel, LikeModel, WatchModel

admin.site.register(ProductModel)
admin.site.register(ShoppingCartModel)
admin.site.register(OrderModel)
admin.site.register(OrderItemModel)
admin.site.register(LikeModel)
admin.site.register(WatchModel)


# Register your models here.
