from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='main'),
    path('register/', views.Register.as_view(), name='register'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('cart/', views.cart, name='cart'),
    path('categories/', views.categories, name='categories'),
    path('categories/<str:category>', views.category, name='category'),
    path('product/<int:pk>', views.ProductView.as_view(), name='product'),
    path('recently_watched/', views.recently_watched, name='recently_watched'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('add_like/', views.add_like, name='add_like'),
    path('remove_like/', views.remove_like, name='remove_like'),
    path('order/', views.order, name='order')
]
