from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path("accounts/register/customer/", views.register_customer, name="register_customer"),
    path("accounts/register/seller/", views.register_seller, name="register_seller"),
    path("accounts/login/", views.user_login, name="login"),
    path("seller/login/", views.seller_login, name="seller_login"),
    path("accounts/login/seller/", views.seller_login, name="seller_login_alias"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("seller/", views.seller_dashboard, name="seller_dashboard"),
    path("seller/products/add/", views.product_create, name="product_create"),
    path("seller/products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("seller/products/<int:pk>/toggle-status/", views.product_toggle_status, name="product_toggle_status"),
    path("seller/products/<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("seller/orders/<int:pk>/status/", views.order_update_status, name="order_update_status"),
    path("cart/", views.cart, name="cart"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:pk>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("my-orders/", views.my_orders, name="my_orders"),
]
