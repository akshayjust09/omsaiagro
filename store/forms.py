from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Product


class RegisterForm(UserCreationForm):
    """Seller registration form (business_name field visible)."""
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "name@example.com"}))
    business_name = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Agro Agency / Farm Store name"}))

    class Meta:
        model = User
        fields = ("username", "email", "business_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class CustomerRegisterForm(UserCreationForm):
    """Customer registration – requires phone + address."""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        "class": "form-control", "placeholder": "name@example.com"
    }))
    phone = forms.CharField(
        max_length=15, required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control", "placeholder": "10-digit mobile number",
            "pattern": "[6-9][0-9]{9}", "title": "Enter a valid 10-digit Indian mobile number"
        })
    )
    address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            "class": "form-control", "rows": 3,
            "placeholder": "House / Flat No., Street, Village, Taluka, District, State - Pincode"
        })
    )

    class Meta:
        model = User
        fields = ("username", "email", "phone", "address", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.phone = self.cleaned_data["phone"]
        user.address = self.cleaned_data["address"]
        if commit:
            user.save()
        return user


class OTPRequestForm(forms.Form):
    """Step 1 of customer OTP login: enter registered mobile / username."""
    username = forms.CharField(
        max_length=150, label="Username or Mobile Number",
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "Enter your username or registered mobile",
            "autofocus": True,
        })
    )


class OTPVerifyForm(forms.Form):
    """Step 2 of customer OTP login: enter the 6-digit OTP."""
    username = forms.CharField(widget=forms.HiddenInput())
    otp_code = forms.CharField(
        max_length=6, min_length=6, label="6-Digit OTP",
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg text-center fs-3 letter-spacing-otp",
            "placeholder": "_ _ _ _ _ _",
            "maxlength": "6",
            "inputmode": "numeric",
            "autocomplete": "one-time-code",
            "autofocus": True,
        })
    )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            "name", "category", "brand", "sku",
            "technical_name", "package_size", "target_crops", "dosage",
            "price", "mrp", "stock", "description",
            "image", "image_url", "is_organic", "is_active"
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
            "image_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://m.media-amazon.com/images/I/..."}),
            "is_organic": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
