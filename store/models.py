from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = [("customer", "Customer"), ("seller", "Seller")]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")
    business_name = models.CharField(max_length=160, blank=True)

    def __str__(self):
        return self.username

class Product(models.Model):
    CATEGORY_CHOICES = [
        ("seeds", "Seeds & Grains (बियाणे)"),
        ("fertilizers", "Fertilizers & Nutrients (खते)"),
        ("pesticides", "Pesticides & Insecticides (कीटकनाशके)"),
        ("fungicides", "Fungicides & Herbicides (बुरशीनाशके / तणनाशके)"),
        ("growth_promoters", "Growth Promoters & Tonics (टॉनिक)"),
        ("irrigation", "Drip & Irrigation Equipment (ठिबक सिंचन)"),
        ("mulching", "Mulching & Shade Nets (मल्चिंग पेपर / शेडनेट)"),
        ("tools", "Farm Tools & Sprayers (शेती अवजारे / स्प्रे पंप)"),
        ("organic", "Organic & Bio Products (सेंद्रिय उत्पादने)"),
        ("other", "Other Agri Essentials (इतर)"),
    ]

    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=200, verbose_name="Product Name")
    sku = models.CharField(max_length=80, unique=True, verbose_name="SKU / Item Code")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="other", verbose_name="Product Category")
    brand = models.CharField(max_length=120, blank=True, verbose_name="Brand / Company")
    technical_name = models.CharField(max_length=255, blank=True, verbose_name="Technical Name / Chemical Formula")
    package_size = models.CharField(max_length=80, blank=True, verbose_name="Packing Size (e.g. 1 kg, 500 ml, 50 kg bag)")
    target_crops = models.CharField(max_length=255, blank=True, verbose_name="Suitable Crops (e.g. Cotton, Soybean, Sugarcane, Vegetables)")
    dosage = models.TextField(blank=True, verbose_name="Dosage & Application Instructions")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Selling Price (₹)")
    mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="MRP (₹)")
    stock = models.PositiveIntegerField(default=0, verbose_name="Available Stock Quantity")
    description = models.TextField(blank=True, verbose_name="Detailed Description / Benefits")
    image = models.ImageField(upload_to="products/", blank=True, null=True, verbose_name="Product Photo")
    image_url = models.TextField(blank=True, verbose_name="Image URL or Encoded Photo")
    is_organic = models.BooleanField(default=False, verbose_name="100% Organic / Bio-certified")
    is_active = models.BooleanField(default=True, verbose_name="Active (Visible in Store)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    @property
    def display_image(self):
        if self.image_url:
            return self.image_url
        if self.image:
            try:
                return self.image.url
            except Exception:
                return None
        return None

    @property
    def discount_percentage(self):
        if self.mrp and self.mrp > self.price:
            return int(round(((self.mrp - self.price) / self.mrp) * 100))
        return 0

class Order(models.Model):
    STATUS_CHOICES = [
        ("placed", "Placed"), ("processing", "Processing"),
        ("shipped", "Shipped"), ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    full_name = models.CharField(max_length=160)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    pincode = models.CharField(max_length=10)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=30, default="COD")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="placed")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sold_items")
    product_name = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
