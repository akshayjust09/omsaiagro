from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Product, Order, OrderItem

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Store details", {"fields": ("role", "business_name")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Store details", {"fields": ("role", "business_name")}),)
    list_display = ("username", "email", "role", "is_staff", "is_active")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "seller", "price", "stock", "is_active")
    search_fields = ("name", "sku")

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "seller", "product_name", "unit_price", "quantity", "line_total")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "total", "status", "created_at")
    list_filter = ("status", "created_at")
    inlines = [OrderItemInline]
