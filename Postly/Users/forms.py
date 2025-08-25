from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "login-input",
            "placeholder": "Username"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "login-input",
            "placeholder": "Password"
        })
    )

class RegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "login-input",
            "placeholder": "Username"
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "login-input",
            "placeholder": "Email"
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "login-input",
            "placeholder": "Password"
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "login-input",
            "placeholder": "Confirm Password"
        })
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "login-input",
            "placeholder": "Old Password"
        })
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "login-input",
            "placeholder": "New Password"
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "login-input",
            "placeholder": "Confirm New Password"
        })
    )
