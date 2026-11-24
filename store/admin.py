from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Product, Order, OrderItem, OTPToken


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Store Details", {"fields": ("role", "business_name", "phone", "address")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Store Details", {"fields": ("role", "business_name", "phone", "address")}),
    )
    list_display = ("username", "email", "role", "phone", "business_name", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email", "phone", "business_name")


@admin.register(OTPToken)
class OTPTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "otp", "purpose", "is_used", "created_at")
    list_filter = ("purpose", "is_used")
    readonly_fields = ("created_at",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "brand", "package_size", "price", "stock", "is_organic", "is_active", "seller")
    list_filter = ("category", "is_organic", "is_active", "created_at")
    search_fields = ("name", "sku", "brand", "technical_name", "target_crops")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "seller", "product_name", "unit_price", "quantity", "line_total")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "total", "status", "payment_method", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    inlines = [OrderItemInline]
