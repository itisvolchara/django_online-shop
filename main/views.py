from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from .models import Product, Order, OrderItem, ShoppingCart, Like, Watch
from .forms import RegisterUserForm, LoginUserForm

from .tasks import send_order_email, send_thankyou_email
from datetime import timedelta
from django.utils import timezone

from django.core.cache import cache


def data_in_cache(key):
    return cache.has_key(key)

def cache_update(request, cache_list):
    for cache_name in cache_list:
        if not data_in_cache(cache_name):
            if cache_name == 'products':
                cache.set(cache_name, Product.objects.all())
            elif cache_name == 'user_product_ids':
                cache.set(cache_name, [obj.product.id for obj in ShoppingCart.objects.filter(customer=request.user.id).select_related('product')])
            elif cache_name == 'user_likes':
                cache.set(cache_name, Like.objects.filter(customer=request.user.id).select_related('product'))
            elif cache_name == 'user_product_likes':
                cache.set(cache_name, [obj.product.id for obj in Like.objects.filter(customer=request.user.id).select_related('product')])
            elif cache_name == 'user_orders':
                cache.set(cache_name, Order.objects.filter(customer=request.user.id))
            elif cache_name == 'user_watches_ids':
                cache.set(cache_name, set([obj.product.id for obj in Watch.objects.filter(customer=request.user.id).select_related('product')]))
            elif cache_name == 'order_items':
                # orderitems = OrderItem.objects.all().select_related('order', 'product')
                # cache.set(cache_name, [obj for obj in orderitems if obj.order.customer.id == request.user.id])
                cache.set(cache_name, list(OrderItem.objects.filter(order__customer_id=request.user.id).select_related('order', 'product')))
            elif cache_name == 'shopping_cart':
                cache.set(cache_name, ShoppingCart.objects.filter(customer=request.user.id).select_related('product'))


def index(request):
    data = {'user': request.user}
    return render(request, 'main/main.html', data)


def categories(request):
    data = {
        'categories': [element[1] for element in Product.CATEGORIES],
        'user': request.user
    }

    return render(request, 'main/categories.html', data)


def category(request, category):
    cache_update(request, ['products', 'user_product_ids', 'user_product_likes'])

    products = cache.get('products').filter(category=Product.CATEGORIES_DIR[category])
    user_product_ids = cache.get('user_product_ids')
    user_product_likes = cache.get('user_product_likes')

    data = {
        'products': products,
        'user_product_ids': user_product_ids,
        'user_product_likes': user_product_likes,
        'category': category,
        'user': request.user
    }

    return render(request, 'main/products.html', data)

def recently_watched(request):
    cache_update(request, ['products', 'user_product_ids', 'user_product_likes', 'user_watches_ids'])

    user_product_ids = cache.get('user_product_ids')
    user_product_likes = cache.get('user_product_likes')
    products = cache.get('products').filter(id__in = cache.get('user_watches_ids'))

    data = {
        'user': request.user,
        'user_product_ids': user_product_ids,
        'user_product_likes': user_product_likes,
        'products': products
    }

    return render(request, 'main/recently_watched_products.html', data)

class ProductView(DetailView):
    model = Product
    template_name = 'main/product.html'
    context_object_name = 'product'

    extra_context = {}

    def get(self, request, *args, **kwargs):
        cache_update(request, ['user_product_ids', 'user_product_likes', 'user_watches_ids'])

        self.extra_context['user'] = request.user
        self.extra_context['user_product_ids'] = cache.get('user_product_ids')
        self.extra_context['user_product_likes'] = cache.get('user_product_likes')

        product = self.get_object()
        user_watches_ids = cache.get('user_watches_ids')
        user_watches_ids.add(product.id)
        cache.set('user_watches_ids', user_watches_ids)

        Watch(customer=request.user, product=product).save()

        return super().get(request, *args, **kwargs)

class Register(CreateView):
    form_class = RegisterUserForm
    template_name = 'main/auth.html'
    success_url = reverse_lazy('main')

    extra_context = {'status': 'register'}

    def dispatch(self, request, *args, **kwargs):
        self.extra_context['user'] = request.user
        return super().dispatch(request)


class Login(LoginView):
    form_class = LoginUserForm
    template_name = 'main/auth.html'

    extra_context = {'status': 'login'}

    def get_success_url(self):
        cache.clear()

        return reverse_lazy('main')

    def dispatch(self, request, *args, **kwargs):
        self.extra_context['user'] = request.user
        return super().dispatch(request)


@login_required
def profile(request):
    cache_update(request, ['order_items'])

    orderitems = cache.get('order_items')


    jsondata = {}
    for obj in orderitems:
        if obj.order.id not in jsondata:
            jsondata[obj.order.id] = {'date': obj.order.date_time, 'total': obj.order.total_price, 'products': []}

        jsondata[obj.order.id]['products'].append(obj.product)

    data = {'user': request.user,
            'orderitems': jsondata
            }

    return render(request, 'main/profile.html', data)


def logout_user(request):
    logout(request)

    #очистка кэша
    cache.clear()

    return redirect('login')


@login_required
def cart(request):
    cache_update(request, ['user_product_ids', 'user_product_likes', 'shopping_cart'])

    products_to_buy = [obj.product for obj in cache.get('shopping_cart')]

    user_product_ids = cache.get('user_product_ids')
    user_product_likes = [id for id in cache.get('user_product_likes')]

    total_price = sum([product.price for product in products_to_buy])

    data = {
        'user': request.user,
        'products': products_to_buy,
        'user_product_ids': user_product_ids,
        'user_product_likes': user_product_likes,
        'total': total_price
    }

    return render(request, 'main/cart.html', data)


@login_required
def order(request):
    cache_update(request, ['shopping_cart', 'user_orders', 'order_items'])

    shopping_cart = cache.get('shopping_cart')
    order_sum = sum([obj.product.price for obj in shopping_cart])

    new_order = Order(customer=request.user, total_price=order_sum)
    new_order.save()

    # сохранение заказа в кэш
    # еще не оптимизировал. И оптимизирую ли вообще?
    cache.set('user_orders', Order.objects.filter(customer=request.user))

    orderitems = cache.get('order_items')

    for obj in shopping_cart:
        new_order_item = OrderItem(order=new_order, product=obj.product)
        new_order_item.save()

        orderitems.append(new_order_item)

        obj.delete()

    # обновление списка купленных товаров
    cache.set('order_items', orderitems)

    # удаление списка покупок из кэша
    cache.delete('shopping_cart')
    cache.delete('user_product_ids')

    send_order_email.delay(request.user.id, [obj.product.name for obj in shopping_cart], order_sum, new_order.id)
    send_thankyou_email.apply_async(args=[request.user.id], eta=timezone.now() + timedelta(minutes=5))

    return redirect('profile')


@login_required
def add_to_cart(request):
    product_id = int(request.GET.get('product_id', None))

    cache_update(request, ['products', 'user_product_ids', 'shopping_cart'])

    shopping_cart = cache.get('shopping_cart')

    response = {}

    if product_id in [obj.product.id for obj in shopping_cart]:
        response['status'] = 'error'
        response['message'] = 'Продукт уже в корзине'
        return JsonResponse(response)

    new_record = ShoppingCart(customer=request.user, product=Product.objects.get(id=product_id))
    new_record.save()

    # пока не оптимизирую
    cache.set('shopping_cart', ShoppingCart.objects.filter(customer=request.user).select_related('product'))

    # кэширование нового списка айди купленных товаров
    new_cache_ids = cache.get('user_product_ids')
    new_cache_ids.append(product_id)
    cache.set('user_product_ids', new_cache_ids)

    response = {
        'status': 'success',
        'message': 'Продукт добавлен в корзину'
    }
    return JsonResponse(response)


@login_required
def remove_from_cart(request):
    product_id = int(request.GET.get('product_id', None))

    cache_update(request, ['products', 'user_product_ids', 'shopping_cart'])

    shopping_cart = cache.get('shopping_cart')

    response = {}

    if product_id not in [obj.product.id for obj in shopping_cart]:
        response['status'] = 'error'
        response['message'] = 'Продукта нет в корзине'
        return JsonResponse(response)

    # Пока никак не оптимизировать
    ShoppingCart.objects.filter(customer=request.user, product=product_id).delete()
    cache.set('shopping_cart', ShoppingCart.objects.filter(customer=request.user).select_related('product'))

    # кэширование нового списка айди купленных товаров
    new_cache_ids = cache.get('user_product_ids')
    new_cache_ids.remove(product_id)
    cache.set('user_product_ids', new_cache_ids)


    response = {
        'status': 'success',
        'message': 'Продукт удалён из корзины'
    }

    return JsonResponse(response)


@login_required
def add_like(request):
    product_id = int(request.GET.get('product_id', None))

    cache_update(request, ['products', 'user_product_likes', 'user_likes'])

    user_likes = cache.get('user_likes')

    response = {}

    if product_id in [obj.product.id for obj in user_likes]:
        response['status'] = 'error'
        response['message'] = 'Лайк уже поставлен'
        return JsonResponse(response)

    new_record = Like(customer=request.user, product=Product.objects.get(id=product_id))
    new_record.save()

    # пока не оптимизирую
    cache.set('user_likes', Like.objects.filter(customer=request.user).select_related('product'))

    # кэширование нового списка айди купленных товаров
    new_cache_likes = cache.get('user_product_likes')
    new_cache_likes.append(product_id)
    cache.set('user_product_likes', new_cache_likes)

    response = {
        'status': 'success',
        'message': 'Лайк поставлен'
    }
    return JsonResponse(response)


@login_required
def remove_like(request):
    product_id = int(request.GET.get('product_id', None))

    cache_update(request, ['products', 'user_product_likes', 'user_likes'])

    user_likes = cache.get('user_likes')

    response = {}

    if product_id not in [obj.product.id for obj in user_likes]:
        response['status'] = 'error'
        response['message'] = 'Лайк удалить не удалось'
        return JsonResponse(response)

    Like.objects.filter(customer=request.user, product=product_id).delete()
    cache.set('user_likes', Like.objects.filter(customer=request.user).select_related('product'))

    # кэширование нового списка айди лайков
    new_cache_likes = cache.get('user_product_likes')
    new_cache_likes.remove(product_id)
    cache.set('user_product_likes', new_cache_likes)

    response = {
        'status': 'success',
        'message': 'Лайк удалён'
    }
    return JsonResponse(response)