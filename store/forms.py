from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Product

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "name@example.com"}))
    business_name = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Agro Agency / Farm Store name"}))

    class Meta:
        model = User
        fields = ("username", "email", "business_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            "name", "category", "brand", "sku",
            "technical_name", "package_size", "target_crops", "dosage",
            "price", "mrp", "stock", "description",
            "image", "is_organic", "is_active"
        )
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Mahyco Cotton Seeds / Coragen / NPK 19-19-19"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "brand": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Bayer, Syngenta, UPL, Mahyco, IFFCO"}),
            "sku": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. AGRO-SED-001"}),
            "technical_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Chlorantraniliprole 18.5% SC / NPK Water Soluble"}),
            "package_size": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 500 ml, 1 kg, 5 kg, 50 kg Bag"}),
            "target_crops": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Cotton, Soybean, Sugarcane, Tomato, Wheat"}),
            "dosage": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "e.g. 60 ml per acre / 2 ml per litre water for foliar spray"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "placeholder": "e.g. 650.00", "step": "0.01"}),
            "mrp": forms.NumberInput(attrs={"class": "form-control", "placeholder": "e.g. 750.00", "step": "0.01"}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "placeholder": "e.g. 50"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Describe benefits, application timing, precautions, safety tips..."}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "is_organic": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
