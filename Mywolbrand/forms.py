from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import ContactMessage, PartnerApplication
from .models import Profile
from .models import SellItem
from django.contrib.auth.models import User
from .models import RenovationRequest, PropertyType



class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "message"]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter your full name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter your email"}),
            "message": forms.Textarea(attrs={"class": "form-control", "placeholder": "Write your message here...", "rows": 4}),
        }



class ProfileUpdateForm(forms.ModelForm):
    phone = forms.CharField(max_length=20, required=False, label="Phone Number")

    class Meta:
        model = Profile
        fields = ['phone']



class SellItemForm(forms.ModelForm):
    class Meta:
        model = SellItem
        fields = [
            "title",
            "description",
            "price",
            "image",
            "ownership_proof",
            "category",
            "location",
            "house_type",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter location"}),
            "house_type": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
        }





class PartnerApplicationForm(forms.ModelForm):
    class Meta:
        model = PartnerApplication
        fields = ["name", "company", "email", "website", "partner_type", "message"]
        




class RenovationRequestForm(forms.ModelForm):
    class Meta:
        model = RenovationRequest
        fields = ["category", "property_type", "full_name", "email", "details"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide property types until a category is chosen
        self.fields["property_type"].queryset = PropertyType.objects.none()

        if "category" in self.data:
            try:
                category_id = int(self.data.get("category"))
                self.fields["property_type"].queryset = PropertyType.objects.filter(category_id=category_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.category:
            self.fields["property_type"].queryset = PropertyType.objects.filter(category=self.instance.category)




