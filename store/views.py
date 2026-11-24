from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import RegisterForm, ProductForm
from .models import Product, Order, OrderItem

def home(request):
    products = Product.objects.filter(is_active=True, stock__gt=0).select_related("seller")
    return render(request, "store/home.html", {"products": products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    return render(request, "store/product_detail.html", {"product": product})

def register_customer(request):
    return register_role(request, "customer")

def register_seller(request):
    return register_role(request, "seller")

def register_role(request, role):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.role = role
        user.save()
        login(request, user)
        messages.success(request, "Your account has been created.")
        return redirect("seller_dashboard" if role == "seller" else "home")
    return render(request, "store/register.html", {"form": form, "role": role})

@login_required
def seller_dashboard(request):
    if request.user.role != "seller" and not request.user.is_staff:
        raise PermissionDenied("Seller account required.")
    products = Product.objects.all() if request.user.is_staff else Product.objects.filter(seller=request.user)
    return render(request, "store/seller_dashboard.html", {"products": products})

@login_required
def product_create(request):
    if request.user.role != "seller" and not request.user.is_staff:
        raise PermissionDenied("Seller account required.")
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)
        product.seller = request.user
        product.save()
        messages.success(request, "Product added.")
        return redirect("seller_dashboard")
    return render(request, "store/product_form.html", {"form": form, "heading": "Add product"})

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if not request.user.is_staff and product.seller_id != request.user.id:
        raise PermissionDenied("You can edit only your own products.")
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Product updated.")
        return redirect("seller_dashboard")
    return render(request, "store/product_form.html", {"form": form, "heading": "Edit product"})

def cart(request):
    cart_data = request.session.get("cart", {})
    items, total = [], Decimal("0.00")
    for product_id, qty in cart_data.items():
        product = Product.objects.filter(pk=product_id, is_active=True).first()
        if product:
            quantity = int(qty)
            line = product.price * quantity
            items.append({"product": product, "quantity": quantity, "line_total": line})
            total += line
    return render(request, "store/cart.html", {"items": items, "total": total})

@require_POST
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    cart_data = request.session.get("cart", {})
    current = int(cart_data.get(str(pk), 0))
    requested = int(request.POST.get("quantity", 1))
    requested = max(1, min(requested, 999))
    cart_data[str(pk)] = min(current + requested, product.stock)
    request.session["cart"] = cart_data
    messages.success(request, "Added to cart.")
    return redirect("cart")

@require_POST
def remove_from_cart(request, pk):
    cart_data = request.session.get("cart", {})
    cart_data.pop(str(pk), None)
    request.session["cart"] = cart_data
    return redirect("cart")

@login_required
def checkout(request):
    cart_data = request.session.get("cart", {})
    if not cart_data:
        messages.info(request, "Your cart is empty.")
        return redirect("cart")
    products = []
    total = Decimal("0.00")
    for product_id, qty in cart_data.items():
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        quantity = int(qty)
        if quantity > product.stock:
            messages.error(request, f"Not enough stock for {product.name}.")
            return redirect("cart")
        products.append((product, quantity))
        total += product.price * quantity
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        pincode = request.POST.get("pincode", "").strip()
        if not all([full_name, phone, address, pincode]):
            messages.error(request, "Please complete all delivery fields.")
            return render(request, "store/checkout.html", {"products": products, "total": total})
        order = Order.objects.create(customer=request.user, full_name=full_name, phone=phone,
                                     address=address, pincode=pincode, total=total, payment_method="COD")
        for product, quantity in products:
            OrderItem.objects.create(order=order, product=product, seller=product.seller,
                product_name=product.name, unit_price=product.price, quantity=quantity,
                line_total=product.price * quantity)
            product.stock -= quantity
            product.save(update_fields=["stock"])
        request.session["cart"] = {}
        messages.success(request, f"Order #{order.pk} placed with Cash on Delivery.")
        return redirect("my_orders")
    return render(request, "store/checkout.html", {"products": products, "total": total})

@login_required
def my_orders(request):
    orders = Order.objects.filter(customer=request.user).prefetch_related("items")
    return render(request, "store/my_orders.html", {"orders": orders})
