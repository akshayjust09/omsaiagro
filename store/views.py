import base64
from datetime import timedelta
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import RegisterForm, ProductForm
from .models import Product, Order, OrderItem

def home(request):
    category = request.GET.get("category", "").strip()
    q = request.GET.get("q", "").strip()
    products = Product.objects.filter(is_active=True, stock__gt=0).select_related("seller")

    if category:
        products = products.filter(category=category)
    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(brand__icontains=q) |
            Q(technical_name__icontains=q) |
            Q(target_crops__icontains=q)
        )

    categories = Product.CATEGORY_CHOICES
    return render(request, "store/home.html", {
        "products": products,
        "categories": categories,
        "selected_category": category,
        "query": q,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, is_active=True, stock__gt=0
    ).exclude(pk=product.pk)[:4]
    return render(request, "store/product_detail.html", {
        "product": product,
        "related_products": related_products,
    })

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

def seller_login(request):
    if request.user.is_authenticated:
        if request.user.role == "seller" or request.user.is_staff:
            return redirect("seller_dashboard")
        return redirect("home")

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome to Seller Central, {user.business_name or user.username}!")
            next_url = request.GET.get("next") or request.POST.get("next")
            if next_url:
                return redirect(next_url)
            if user.role == "seller" or user.is_staff:
                return redirect("seller_dashboard")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password. Please verify your seller credentials.")

    return render(request, "store/seller_login.html", {"form": form})

def user_login(request):
    if request.user.is_authenticated:
        if request.user.role == "seller" or request.user.is_staff:
            return redirect("seller_dashboard")
        return redirect("home")

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get("next") or request.POST.get("next")
            if next_url:
                return redirect(next_url)
            if user.role == "seller" or user.is_staff:
                return redirect("seller_dashboard")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "store/login.html", {"form": form})

@login_required
def seller_dashboard(request):
    if request.user.role != "seller" and not request.user.is_staff:
        raise PermissionDenied("Seller account required.")

    # Determine tab
    tab = request.GET.get("tab", "overview").strip().lower()
    if tab not in ["overview", "inventory", "orders", "reports"]:
        tab = "overview"

    # Base querysets
    seller_products = Product.objects.all() if request.user.is_staff else Product.objects.filter(seller=request.user)
    seller_items = OrderItem.objects.all() if request.user.is_staff else OrderItem.objects.filter(seller=request.user)
    seller_orders = Order.objects.filter(items__in=seller_items).distinct().prefetch_related("items").order_by("-created_at")

    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)

    # Sales Performance Metrics (Amazon Sales Snapshot)
    today_items = seller_items.filter(order__created_at__gte=today_start)
    today_sales = sum((item.line_total for item in today_items), Decimal("0.00"))
    today_units = sum((item.quantity for item in today_items), 0)

    seven_day_items = seller_items.filter(order__created_at__gte=seven_days_ago)
    seven_day_sales = sum((item.line_total for item in seven_day_items), Decimal("0.00"))
    seven_day_units = sum((item.quantity for item in seven_day_items), 0)

    thirty_day_items = seller_items.filter(order__created_at__gte=thirty_days_ago)
    thirty_day_sales = sum((item.line_total for item in thirty_day_items), Decimal("0.00"))
    thirty_day_units = sum((item.quantity for item in thirty_day_items), 0)

    total_sales = sum((item.line_total for item in seller_items), Decimal("0.00"))
    total_units_sold = sum((item.quantity for item in seller_items), 0)

    # Order Status Metrics
    pending_orders_count = seller_orders.filter(status__in=["placed", "processing"]).count()
    shipped_orders_count = seller_orders.filter(status="shipped").count()
    delivered_orders_count = seller_orders.filter(status="delivered").count()
    cancelled_orders_count = seller_orders.filter(status="cancelled").count()

    # Inventory Metrics (Amazon Inventory Health)
    total_products = seller_products.count()
    active_listings = seller_products.filter(is_active=True).count()
    inactive_listings = seller_products.filter(is_active=False).count()
    low_stock_count = seller_products.filter(stock__lte=5, stock__gt=0).count()
    out_of_stock_count = seller_products.filter(stock=0).count()
    total_stock_units = sum((p.stock for p in seller_products), 0)
    total_inventory_val = sum((p.price * p.stock for p in seller_products), Decimal("0.00"))

    # Filtering for Inventory Tab
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    status_filter = request.GET.get("status", "").strip()

    filtered_products = seller_products
    if q:
        filtered_products = filtered_products.filter(
            Q(name__icontains=q) |
            Q(sku__icontains=q) |
            Q(brand__icontains=q) |
            Q(technical_name__icontains=q)
        )
    if category:
        filtered_products = filtered_products.filter(category=category)
    if status_filter == "active":
        filtered_products = filtered_products.filter(is_active=True)
    elif status_filter == "inactive":
        filtered_products = filtered_products.filter(is_active=False)
    elif status_filter == "low_stock":
        filtered_products = filtered_products.filter(stock__lte=5, stock__gt=0)
    elif status_filter == "out_of_stock":
        filtered_products = filtered_products.filter(stock=0)

    # Filter for Orders Tab
    order_status_filter = request.GET.get("order_status", "").strip()
    filtered_orders = seller_orders
    if order_status_filter:
        filtered_orders = filtered_orders.filter(status=order_status_filter)
    if q and tab == "orders":
        filtered_orders = filtered_orders.filter(
            Q(id__icontains=q) |
            Q(full_name__icontains=q) |
            Q(phone__icontains=q) |
            Q(address__icontains=q)
        )

    recent_orders = seller_orders[:8]
    top_selling_items = seller_items.values("product__name", "product__sku").annotate(
        units=Sum("quantity"), revenue=Sum("line_total")
    ).order_by("-units")[:5]

    return render(request, "store/seller_dashboard.html", {
        "tab": tab,
        # Performance
        "today_sales": today_sales,
        "today_units": today_units,
        "seven_day_sales": seven_day_sales,
        "seven_day_units": seven_day_units,
        "thirty_day_sales": thirty_day_sales,
        "thirty_day_units": thirty_day_units,
        "total_sales": total_sales,
        "total_units_sold": total_units_sold,
        # Orders
        "seller_orders": filtered_orders,
        "recent_orders": recent_orders,
        "pending_orders_count": pending_orders_count,
        "shipped_orders_count": shipped_orders_count,
        "delivered_orders_count": delivered_orders_count,
        "cancelled_orders_count": cancelled_orders_count,
        "order_status_filter": order_status_filter,
        # Inventory
        "products": filtered_products,
        "total_products": total_products,
        "active_listings": active_listings,
        "inactive_listings": inactive_listings,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "total_stock_units": total_stock_units,
        "total_inventory_val": total_inventory_val,
        "top_selling_items": top_selling_items,
        # Filters
        "categories": Product.CATEGORY_CHOICES,
        "selected_category": category,
        "selected_status": status_filter,
        "query": q,
    })

@login_required
@require_POST
def product_toggle_status(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if not request.user.is_staff and product.seller_id != request.user.id:
        raise PermissionDenied("Unauthorized.")
    product.is_active = not product.is_active
    product.save(update_fields=["is_active"])
    status_label = "Active (Live)" if product.is_active else "Inactive (Hidden)"
    messages.success(request, f"Listing '{product.name}' status changed to {status_label}.")
    return redirect(f"{request.META.get('HTTP_REFERER', '/seller/')}?tab=inventory")

@login_required
@require_POST
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if not request.user.is_staff and product.seller_id != request.user.id:
        raise PermissionDenied("Unauthorized.")
    name = product.name
    product.delete()
    messages.success(request, f"Product '{name}' has been deleted from your catalog.")
    return redirect("/seller/?tab=inventory")

@login_required
@require_POST
def order_update_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    new_status = request.POST.get("status", "").strip()
    valid_statuses = dict(Order.STATUS_CHOICES)
    if new_status in valid_statuses:
        order.status = new_status
        order.save(update_fields=["status"])
        messages.success(request, f"Order #{order.pk} status updated to '{valid_statuses[new_status]}'.")
    return redirect(f"{request.META.get('HTTP_REFERER', '/seller/')}?tab=orders")

def _handle_product_media(product, uploaded_file):
    if uploaded_file:
        try:
            content = uploaded_file.read()
            content_type = getattr(uploaded_file, "content_type", "") or "image/jpeg"
            b64_str = base64.b64encode(content).decode("utf-8")
            product.image_url = f"data:{content_type};base64,{b64_str}"
            product.image = None
        except Exception:
            pass

@login_required
def product_create(request):
    if request.user.role != "seller" and not request.user.is_staff:
        raise PermissionDenied("Seller account required.")
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)
        product.seller = request.user
        _handle_product_media(product, request.FILES.get("image"))
        product.save()
        messages.success(request, f"Product '{product.name}' has been added to your Amazon-style catalog.")
        return redirect("/seller/?tab=inventory")
    return render(request, "store/product_form.html", {"form": form, "heading": "Add a Product"})

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if not request.user.is_staff and product.seller_id != request.user.id:
        raise PermissionDenied("You can edit only your own products.")
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)
        _handle_product_media(product, request.FILES.get("image"))
        product.save()
        messages.success(request, f"Listing for '{product.name}' updated successfully.")
        return redirect("/seller/?tab=inventory")
    return render(request, "store/product_form.html", {
        "form": form,
        "heading": f"Edit Listing: {product.name}",
        "product": product,
    })

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
    messages.success(request, f"Added {product.name} to cart.")
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
