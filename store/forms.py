from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Product

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)
    business_name = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "business_name", "password1", "password2")

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("name", "sku", "description", "price", "stock", "image", "is_active")
