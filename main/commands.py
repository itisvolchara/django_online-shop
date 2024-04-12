from abc import ABC, abstractmethod

from main.models import *


class BaseCommand(ABC):

    @staticmethod
    @abstractmethod
    def fill_cache(cache, user_id):
        pass


class ProductCommand(BaseCommand):
    @staticmethod
    def fill_cache(cache, user_id):
        cache.set('products', ProductModel.objects.all())

class UserProductIdsCommand(BaseCommand):

    @staticmethod
    def fill_cache(cache, user_id):
        cache.set('user_product_ids', [obj.product.id for obj in
                                       ShoppingCartModel.objects.filter(customer=user_id).select_related('product')])
        print('Heeeeeyyyy')

class UserLikesCommand(BaseCommand):

    @staticmethod
    def fill_cache(cache, user_id):
        cache.set('user_likes', LikeModel.objects.filter(customer=user_id).select_related('product'))
class UserProductLikesCommand(BaseCommand):

    @staticmethod
    def fill_cache(cache, user_id):
        cache.set('user_product_likes', [obj.product.id for obj in
                                         LikeModel.objects.filter(customer=user_id).select_related('product')])


class UserOrdersCommand(BaseCommand):

    @staticmethod
    def fill_cache(cache, user_id):
        cache.set('user_orders', OrderModel.objects.filter(customer=user_id))


class UserWatchesIdsCommand(BaseCommand):

    @staticmethod
    def fill_cache(cache, user_id):
        cache.set('user_watches_ids', set([obj.product.id for obj in
                                           WatchModel.objects.filter(customer=user_id).select_related('product')]))


class OrderItemsCommand(BaseCommand):

    @staticmethod
    def fill_cache(cache, user_id):
        cache.set('order_items', list(OrderItemModel.objects.filter(order__customer_id=user_id)
                                      .select_related('order', 'product')))

class ShoppingCartCommand(BaseCommand):

    @staticmethod
    def fill_cache(cache, user_id):
        cache.set('shopping_cart', ShoppingCartModel.objects.filter(customer=user_id).select_related('product'))
