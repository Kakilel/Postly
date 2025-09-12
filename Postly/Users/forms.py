from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .models import CustomUser


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


class CustomRegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "login-input",
            "placeholder": "Password"
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            "class": "login-input",
            "placeholder": "Confirm Password"
        })
    )

    class Meta:
        model = CustomUser
        fields = ["username", "email", "full_name", "bio", "profile_image"]

        widgets = {
            "username": forms.TextInput(attrs={
                "class": "login-input",
                "placeholder": "Username"
            }),
            "email": forms.EmailInput(attrs={
                "class": "login-input",
                "placeholder": "Email"
            }),
            "full_name": forms.TextInput(attrs={
                "class": "login-input",
                "placeholder": "Full Name"
            }),
            "bio": forms.Textarea(attrs={
                "class": "login-input",
                "placeholder": "Tell us about yourself"
            }),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


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
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "full_name", "bio", "profile_image"]

        widgets = {
            "username": forms.TextInput(attrs={
                "class": "login-input",
                "placeholder": "Username"
            }),
            "email": forms.EmailInput(attrs={
                "class": "login-input",
                "placeholder": "Email"
            }),
            "full_name": forms.TextInput(attrs={
                "class": "login-input",
                "placeholder": "Full Name"
            }),
            "bio": forms.Textarea(attrs={
                "class": "login-input",
                "placeholder": "Tell us about yourself"
            }),
        }
