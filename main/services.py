from django.utils import timezone

from datetime import timedelta
from abc import ABC, abstractmethod

from .cache import Cache
from .models import *
from .specialclasses import Singleton
from .tasks import send_order_email, send_thankyou_email


class BaseService(Singleton):

    def __init__(self):
        self.cache = Cache()
        self.data = None


class HandlerService(BaseService):

    @abstractmethod
    def handle(self, *args):
        pass

    def get_data(self):
        if not self.data:
            raise ValueError("There's no data to hand over")
        return self.data


class LikeService(BaseService):

    def add_like(self, request, product_id):
        self.cache.update(request, ['products', 'user_product_likes', 'user_likes'])

        user_product_likes = self.cache.get('user_product_likes')
        print(user_product_likes)

        response = {}

        if product_id in user_product_likes:
            response['status'] = 'error'
            response['message'] = 'Лайк уже поставлен'
            return response

        new_record = LikeModel(customer=request.user, product=ProductModel.objects.get(id=product_id))
        new_record.save()

        # пока не оптимизирую
        self.cache.set('user_likes', LikeModel.objects.filter(customer=request.user).select_related('product'))

        # кэширование нового списка айди купленных товаров
        new_cache_likes = user_product_likes
        new_cache_likes.append(product_id)
        self.cache.set('user_product_likes', new_cache_likes)

        response = {
            'status': 'success',
            'message': 'Лайк поставлен'
        }

        return response

    def remove_like(self, request, product_id):
        self.cache.update(request, ['products', 'user_product_likes', 'user_likes'])

        user_product_likes = self.cache.get('user_product_likes')

        response = {}

        if product_id not in user_product_likes:
            response['status'] = 'error'
            response['message'] = 'Лайк удалить не удалось'
            return response

        LikeModel.objects.filter(customer=request.user, product=product_id).delete()
        self.cache.set('user_likes', LikeModel.objects.filter(customer=request.user).select_related('product'))

        # кэширование нового списка айди лайков
        new_cache_likes = user_product_likes
        new_cache_likes.remove(product_id)
        self.cache.set('user_product_likes', new_cache_likes)

        response = {
            'status': 'success',
            'message': 'Лайк удалён'
        }

        return response


class CartService(HandlerService):

    def handle(self, request):
        self.cache.update(request, ['user_product_ids', 'user_product_likes', 'shopping_cart'])

        products_to_buy = [obj.product for obj in self.cache.get('shopping_cart')]
        user_product_ids = self.cache.get('user_product_ids')
        user_product_likes = self.cache.get('user_product_likes')
        total_price = sum([product.price for product in products_to_buy])

        self.data = {
            'products': products_to_buy,
            'user_product_ids': user_product_ids,
            'user_product_likes': user_product_likes,
            'total': total_price
        }

    def add_to_cart(self, request, product_id):
        self.cache.update(request, ['products', 'user_product_ids', 'shopping_cart'])

        user_product_ids = self.cache.get('user_product_ids')

        response = {}

        if product_id in user_product_ids:
            response['status'] = 'error'
            response['message'] = 'Продукт уже в корзине'
            return response

        new_record = ShoppingCartModel(customer=request.user, product=ProductModel.objects.get(id=product_id))
        new_record.save()

        # пока не оптимизирую
        self.cache.set('shopping_cart', ShoppingCartModel.objects.filter(customer=request.user).select_related('product'))

        # кэширование нового списка айди купленных товаров
        new_cache_ids = user_product_ids
        new_cache_ids.append(product_id)
        self.cache.set('user_product_ids', new_cache_ids)

        response = {
            'status': 'success',
            'message': 'Продукт добавлен в корзину'
        }

        return response

    def remove_from_cart(self, request, product_id):
        self.cache.update(request, ['products', 'user_product_ids', 'shopping_cart'])

        user_product_ids = self.cache.get('user_product_ids')

        response = {}

        if product_id not in user_product_ids:
            response['status'] = 'error'
            response['message'] = 'Продукта нет в корзине'
            return response

        # Пока никак не оптимизировать
        ShoppingCartModel.objects.filter(customer=request.user, product=product_id).delete()
        self.cache.set('shopping_cart', ShoppingCartModel.objects.filter(customer=request.user).select_related('product'))

        # кэширование нового списка айди купленных товаров
        new_cache_ids = user_product_ids
        new_cache_ids.remove(product_id)
        self.cache.set('user_product_ids', new_cache_ids)

        response = {
            'status': 'success',
            'message': 'Продукт удалён из корзины'
        }

        return response


class ProfileService(HandlerService):

    def handle(self, request):
        self.cache.update(request, ['order_items'])

        orderitems = self.cache.get('order_items')

        jsondata = {}
        for obj in orderitems:
            if obj.order.id not in jsondata:
                jsondata[obj.order.id] = {'date': obj.order.date_time, 'total': obj.order.total_price, 'products': []}

            jsondata[obj.order.id]['products'].append(obj.product)

        self.data = {'orderitems': jsondata}


class LoginService(HandlerService):

    def handle(self):
        self.cache.clear()


class ProductGetService(HandlerService):

    def handle(self, request, product):
        self.cache.update(request, ['user_product_ids', 'user_product_likes', 'user_watches_ids'])

        user_watches_ids = self.cache.get('user_watches_ids')
        user_watches_ids.add(product.id)
        self.cache.set('user_watches_ids', user_watches_ids)

        WatchModel(customer=request.user, product=product).save()

        user_product_ids = self.cache.get('user_product_ids')
        user_product_likes = self.cache.get('user_product_likes')

        self.data = {
            'user_product_ids': user_product_ids,
            'user_product_likes': user_product_likes
        }


class RecentlyWatchedService(HandlerService):

    def handle(self, request):

        self.cache.update(request, ['products', 'user_product_ids', 'user_product_likes', 'user_watches_ids'])

        user_product_ids = self.cache.get('user_product_ids')
        user_product_likes = self.cache.get('user_product_likes')
        products = self.cache.get('products').filter(id__in=self.cache.get('user_watches_ids'))

        self.data = {
            'user_product_ids': user_product_ids,
            'user_product_likes': user_product_likes,
            'products': products
        }


class CategoryService(HandlerService):

    def handle(self, request, category):
        self.cache.update(request, ['products', 'user_product_ids', 'user_product_likes'])

        products = self.cache.get('products').filter(category=ProductModel.CATEGORIES_DIR[category])
        user_product_ids = self.cache.get('user_product_ids')
        user_product_likes = self.cache.get('user_product_likes')

        self.data = {
            'products': products,
            'user_product_ids': user_product_ids,
            'user_product_likes': user_product_likes
        }


class OrderService(BaseService):

    def order(self, request):
        self.cache.update(request, ['shopping_cart', 'user_orders', 'order_items'])

        shopping_cart = self.cache.get('shopping_cart')
        order_sum = sum([obj.product.price for obj in shopping_cart])

        new_order = OrderModel(customer=request.user, total_price=order_sum)
        new_order.save()

        # сохранение заказа в кэш
        # еще не оптимизировал. И оптимизирую ли вообще?
        self.cache.set('user_orders', OrderModel.objects.filter(customer=request.user))

        orderitems = self.cache.get('order_items')

        for obj in shopping_cart:
            new_order_item = OrderItemModel(order=new_order, product=obj.product)
            new_order_item.save()

            orderitems.append(new_order_item)

            obj.delete()

        # обновление списка купленных товаров
        self.cache.set('order_items', orderitems)

        # удаление списка покупок из кэша
        self.cache.delete('shopping_cart')
        self.cache.delete('user_product_ids')

        send_order_email.delay(request.user.id, [obj.product.name for obj in shopping_cart], order_sum, new_order.id)
        send_thankyou_email.apply_async(args=[request.user.id], eta=timezone.now() + timedelta(minutes=5))