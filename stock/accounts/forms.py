from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile, Customer, Vendor


class CreateUserForm(UserCreationForm):
    """Form for creating a new user with an email field."""
    email = forms.EmailField()

    class Meta:
        """Meta options for the CreateUserForm."""
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2'
        ]


class UserUpdateForm(forms.ModelForm):
    """Form for updating existing user information."""
    class Meta:
        """Meta options for the UserUpdateForm."""
        model = User
        fields = [
            'username',
            'email'
        ]


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile information."""
    class Meta:
        """Meta options for the ProfileUpdateForm."""
        model = Profile
        fields = [
            'telephone',
            'email',
            'first_name',
            'last_name',
            'profile_picture'
        ]


class CustomerForm(forms.ModelForm):
    """Form for creating/updating customer information."""
    class Meta:
        model = Customer
        fields = [
            'first_name',
            'last_name',
            'address',
            'email',
            'phone',
            'loyalty_points'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le Prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le Nom'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez Adresse',
                'rows': 3
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez Email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez Numéro de téléphone'
            }),
            'loyalty_points': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez les points de fidélité'
            }),
        }


class VendorForm(forms.ModelForm):
    """Form for creating/updating vendor information."""
    class Meta:
        model = Vendor
        fields = ['name', 'phone_number', 'address']
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Entrez le nom du fournisseur'}
            ),
            'phone_number': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Entrez le numéro de Téléphone'}
            ),
            'address': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Entrez Adresse'}
            ),
        }