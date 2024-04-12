from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from .forms import RegisterUserForm, LoginUserForm
from .services import *


def index(request):
    data = {'user': request.user}
    return render(request, 'main/main.html', data)


def categories(request):

    data = {
        'categories': [element[1] for element in ProductModel.CATEGORIES],
        'user': request.user
    }

    return render(request, 'main/categories.html', data)


def category(request, category):

    service = CategoryService()
    service.handle(request, category)

    data = {
        'category': category,
        'user': request.user
    }

    data.update(service.get_data())

    return render(request, 'main/products.html', data)


def recently_watched(request):

    service = RecentlyWatchedService()
    service.handle(request)

    data = {
        'user': request.user,
    }

    data.update(service.get_data())

    return render(request, 'main/recently_watched_products.html', data)


class ProductView(DetailView):
    model = ProductModel
    template_name = 'main/product.html'
    context_object_name = 'product'

    extra_context = {}

    def get(self, request, *args, **kwargs):

        service = ProductGetService()
        service.handle(request, self.get_object())

        self.extra_context['user'] = request.user
        self.extra_context.update(service.get_data())

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
        LoginService().handle()

        return reverse_lazy('main')

    def dispatch(self, request, *args, **kwargs):
        self.extra_context['user'] = request.user
        return super().dispatch(request)


@login_required
def profile(request):

    service = ProfileService()
    service.handle(request)

    data = {'user': request.user}
    data.update(service.get_data())

    return render(request, 'main/profile.html', data)


def logout_user(request):
    logout(request)

    #очистка кэша
    LoginService().handle()

    return redirect('login')


@login_required
def cart(request):

    service = CartService()
    service.handle(request)

    data = {
        'user': request.user,
    }

    data.update(service.get_data())

    return render(request, 'main/cart.html', data)


@login_required
def order(request):

    service = OrderService()
    service.order(request)

    return redirect('profile')


@login_required
def add_to_cart(request):
    product_id = int(request.GET.get('product_id', None))

    response = CartService().add_to_cart(request, product_id)

    return JsonResponse(response)


@login_required
def remove_from_cart(request):
    product_id = int(request.GET.get('product_id', None))

    response = CartService().remove_from_cart(request, product_id)

    return JsonResponse(response)


@login_required
def add_like(request):
    product_id = int(request.GET.get('product_id', None))

    response = LikeService().add_like(request, product_id)

    return JsonResponse(response)


@login_required
def remove_like(request):
    product_id = int(request.GET.get('product_id', None))

    response = LikeService().remove_like(request, product_id)

    return JsonResponse(response)