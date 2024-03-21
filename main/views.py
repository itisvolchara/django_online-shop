from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .models import Product, Order, OrderItem, ShoppingCart, Like
from .forms import RegisterUserForm, LoginUserForm


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
    products = Product.objects.filter(category=Product.CATEGORIES_DIR[category])
    user_product_ids = [obj.product.id for obj in ShoppingCart.objects.filter(customer=request.user.id)]
    user_product_likes = [obj.product.id for obj in Like.objects.filter(customer=request.user.id)]

    print(user_product_ids)

    data = {
        'products': products,
        'user_product_ids': user_product_ids,
        'user_product_likes': user_product_likes,
        'category': category,
        'user': request.user
    }

    return render(request, 'main/products.html', data)


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
        return reverse_lazy('main')

    def dispatch(self, request, *args, **kwargs):
        self.extra_context['user'] = request.user
        return super().dispatch(request)


@login_required
def profile(request):
    orderitems = OrderItem.objects.all().select_related('order', 'product')
    orderitems = [obj for obj in orderitems if obj.order.customer.id == request.user.id]

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
    return redirect('login')


@login_required
def cart(request):
    products_to_buy = [obj.product for obj in
                       ShoppingCart.objects.filter(customer=request.user).select_related('product')]
    user_product_ids = [obj.product.id for obj in ShoppingCart.objects.filter(customer=request.user.id)]

    total_price = sum([product.price for product in products_to_buy])

    data = {
        'user': request.user,
        'products': products_to_buy,
        'user_product_ids': user_product_ids,
        'total': total_price
    }

    return render(request, 'main/cart.html', data)


@login_required
def order(request):
    shopping_cart = ShoppingCart.objects.filter(customer=request.user).select_related('product')
    order_sum = sum([obj.product.price for obj in shopping_cart])

    new_order = Order(customer=request.user, total_price=order_sum)
    new_order.save()

    for obj in shopping_cart:
        new_order_item = OrderItem(order=new_order, product=obj.product)
        new_order_item.save()
        obj.delete()

    print(new_order.id)

    return redirect('profile')


@login_required
def add_to_cart(request):
    product_id = request.GET.get('product_id', None)
    shopping_cart = ShoppingCart.objects.filter(customer=request.user).select_related('product')

    response = {}

    if int(product_id) in [obj.product.id for obj in shopping_cart]:
        response['status'] = 'error'
        response['message'] = 'Продукт уже в корзине'
        return JsonResponse(response)

    new_record = ShoppingCart(customer=request.user, product=Product.objects.filter(id=product_id).first())
    new_record.save()

    print(product_id)
    response = {
        'status': 'success',
        'message': 'Продукт добавлен в корзину'
    }
    return JsonResponse(response)


@login_required
def remove_from_cart(request):
    product_id = request.GET.get('product_id', None)
    shopping_cart = ShoppingCart.objects.filter(customer=request.user).select_related('product')

    response = {}

    if int(product_id) not in [obj.product.id for obj in shopping_cart]:
        response['status'] = 'error'
        response['message'] = 'Продукта нет в корзине'
        return JsonResponse(response)

    ShoppingCart.objects.filter(customer=request.user, product=Product.objects.get(id=product_id)).delete()

    print(product_id)

    response = {
        'status': 'success',
        'message': 'Продукт удалён из корзины'
    }
    return JsonResponse(response)


@login_required
def add_like(request):
    product_id = request.GET.get('product_id', None)
    user_likes = Like.objects.filter(customer=request.user).select_related('product')

    response = {}

    if int(product_id) in [obj.product.id for obj in user_likes]:
        response['status'] = 'error'
        response['message'] = 'Лайк уже поставлен'
        return JsonResponse(response)

    new_record = Like(customer=request.user, product=Product.objects.filter(id=product_id).first())
    new_record.save()

    print(product_id)
    response = {
        'status': 'success',
        'message': 'Лайк поставлен'
    }
    return JsonResponse(response)


@login_required
def remove_like(request):
    product_id = request.GET.get('product_id', None)
    user_likes = Like.objects.filter(customer=request.user).select_related('product')

    response = {}

    if int(product_id) not in [obj.product.id for obj in user_likes]:
        response['status'] = 'error'
        response['message'] = 'Лайк удалить не удалось'
        return JsonResponse(response)

    Like.objects.filter(customer=request.user, product=Product.objects.get(id=product_id)).delete()

    print(product_id)

    response = {
        'status': 'success',
        'message': 'Лайк удалён'
    }
    return JsonResponse(response)
