from django.core.cache import cache

from .commands import *
from .specialclasses import Singleton


class Cache(Singleton):

    COMMANDS = {
        'products': ProductCommand,
        'user_product_ids': UserProductIdsCommand,
        'user_likes': UserLikesCommand,
        'user_product_likes': UserProductLikesCommand,
        'user_orders': UserOrdersCommand,
        'user_watches_ids': UserWatchesIdsCommand,
        'order_items': OrderItemsCommand,
        'shopping_cart': ShoppingCartCommand
    }
    @staticmethod
    def find(cache_key):
        return cache.has_key(cache_key)
    @staticmethod
    def get(cache_key):
        return cache.get(cache_key)

    @staticmethod
    def set(cache_key, value):
        cache.set(cache_key, value)

    @staticmethod
    def delete(cache_key):
        cache.delete(cache_key)

    @staticmethod
    def clear():
        cache.clear()

    def update(self, request, cache_list):
        for cache_name in cache_list:
            if not self.find(cache_name):
                self.COMMANDS.get(cache_name).fill_cache(self, request.user.id)
