from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page),
    path('product/<int:pk>', views.product_page),
    path('category/<int:pk>', views.category_page),
    path('search/', views.Search.as_view()),
    path('register', views.Register.as_view()),
    path('logout', views.logout_view),
    path('to-cart/<int:pk>', views.to_cart),
    path('cart', views.cart),
    path('del-from-cart/<int:pk>', views.del_from_cart)
]