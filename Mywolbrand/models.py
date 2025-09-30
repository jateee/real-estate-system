from django.db import models
from django.contrib.auth.models import User
from django import forms
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings



class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, blank=True, null=True)
    id_card = models.FileField(upload_to="id_cards/", blank=True, null=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class SellItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sell_items")
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    commission = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    final_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    image = models.ImageField(upload_to="property_images/")
    is_sold = models.BooleanField(default=False)
    ownership_proof = models.FileField(upload_to="ownership_proofs/", blank=True, null=True)

    category = models.CharField(
        max_length=100,
        choices=[
            ("residential", "Residential"),
            ("commercial", "Commercial"),
            ("land", "Land"),
            ("other", "Other"),
        ],
        default="other"
    )

    location = models.CharField(max_length=255, default="unknown")

    house_type = models.CharField(
        max_length=100,
        choices=[
            ("apartment", "Apartment"),
            ("bungalow", "Bungalow"),
            ("villa", "Villa"),
            ("duplex", "Duplex"),
            ("mansion", "Mansion"),
            ("other", "Other"),
        ],
        default="other"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.price:
            commission_rate = Decimal("0.10") 
            self.commission = self.price * commission_rate
            self.final_price = self.price + self.commission
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone = forms.CharField(required=True)
    id_card = forms.FileField(required=True)

    class Meta:
        model = Profile
        fields = ["phone", "id_card"]

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = self.instance.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            profile.save()
        return profile


class Property(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True, blank=True)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True, blank=True)
    image = models.ImageField(upload_to="properties/")
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        if self.price is not None:
            commission_val = (self.price * Decimal("0.10")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            self.commission = commission_val
            self.final_price = (self.price + commission_val).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class PartnerApplication(models.Model):
    PARTNER_TYPES = [
        ("reseller", "Reseller"),
        ("affiliate", "Affiliate"),
        ("sponsor", "Sponsor"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=150)
    company = models.CharField(max_length=150, blank=True)
    email = models.EmailField()
    website = models.URLField(blank=True)
    partner_type = models.CharField(max_length=50, choices=PARTNER_TYPES)
    message = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.partner_type}"


class PropertyCategory(models.Model):
    CATEGORY_CHOICES = [
        ("residential", "Residential"),
        ("commercial", "Commercial"),
        ("land", "Land"),
    ]
    slug = models.SlugField(max_length=50, unique=True, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Property Categories"

    def __str__(self):
        return self.name


class PropertyType(models.Model):
    category = models.ForeignKey(PropertyCategory, on_delete=models.CASCADE, related_name="types")
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Property Types"

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class RenovationRequest(models.Model):
    category = models.ForeignKey(PropertyCategory, on_delete=models.SET_NULL, null=True)
    property_type = models.ForeignKey(PropertyType, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.category.name}"


class PropertyDevelopmentRequest(models.Model):
    PROPERTY_TYPES = [
        ("residential", "Residential"),
        ("commercial", "Commercial"),
        ("land", "Land"),
    ]

    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    residential_type = models.CharField(max_length=50, blank=True, null=True)
    commercial_type = models.CharField(max_length=50, blank=True, null=True)
    land_type = models.CharField(max_length=50, blank=True, null=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True) 
    details = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.property_type}"




class UserConsent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="consent")
    cookie_consent = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {'Accepted' if self.cookie_consent else 'Declined'}"





class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey("SellItem", on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} added {self.property.title} to cart"





class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(SellItem, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected")],
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.user.username} bid {self.amount} on {self.property.title}"




class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    


class LoginActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    browser = models.CharField(max_length=100, blank=True, null=True)
    os = models.CharField(max_length=100, blank=True, null=True)
    device_type = models.CharField(max_length=50, blank=True, null=True)
    attempted_user = models.CharField(max_length=255, blank=True, null=True)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(blank=True, null=True)
    login_success = models.BooleanField(default=True)  

    def __str__(self):
        return f"{self.user} - {self.ip_address} ({'Success' if self.login_success else 'Failed'})"



