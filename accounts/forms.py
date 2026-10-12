from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import CustomerProfile


class RegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Full name"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email address"}))
    mobile_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "+91 XXXXX XXXXX"}))

    class Meta:
        model = User
        fields = ("username", "email", "full_name", "mobile_number", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({"class": "form-control", "placeholder": "Password"})
        self.fields["password2"].widget.attrs.update({"class": "form-control", "placeholder": "Confirm password"})

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower()
        if commit:
            user.save()
            CustomerProfile.objects.create(
                user=user,
                full_name=self.cleaned_data["full_name"],
                mobile_number=self.cleaned_data["mobile_number"],
            )
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control", "placeholder": "Username or email"})
        self.fields["password"].widget.attrs.update({"class": "form-control", "placeholder": "Password"})


class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))

    class Meta:
        model = CustomerProfile
        fields = ("full_name", "mobile_number")
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "mobile_number": forms.TextInput(attrs={"class": "form-control"}),
        }
