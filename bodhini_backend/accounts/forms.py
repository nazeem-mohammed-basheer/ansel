# bodhini_backend/accounts/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Profile

# 1. User Registration Form (Re-added)
class UserRegisterForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Choose a Username'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Create a Password'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = User
        fields = ['username', 'email'] # Password fields are handled manually for confirmation

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password and password2 and password != password2:
            self.add_error('password2', 'Passwords do not match.')
        return cleaned_data


# User Update Form (Already present, no changes needed)
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

# Profile Update Form (Updated to include 'bio')
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        # Now includes 'bio' so users can update it
        fields = ['image', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us a little about yourself...'}),
        }

# Contact Form (Already present, no changes needed)
class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Your Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Your Email'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Your Message', 'rows': 5})
    )