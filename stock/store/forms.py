from django import forms
from .models import Item, Category, Delivery


class ItemForm(forms.ModelForm):
    """
    A form for creating or updating an Item in the inventory.
    """
    class Meta:
        model = Item
        fields = [
            'name',
            'description',
            'category',
            'quantity',
            'price',  # Ce champ sera utilisé pour le prix d'achat
            'expiring_date',
            'vendor'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 2
                }
            ),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01'
                }
            ),
            'expiring_date': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local'
                }
            ),
            'vendor': forms.Select(attrs={'class': 'form-control'}),
        }


class CategoryForm(forms.ModelForm):
    """
    A form for creating or updating category.
    """
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name',
                'aria-label': 'Category Name'
            }),
        }
        labels = {
            'name': 'Category Name',
        }


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = [
            'item',
            'customer_name',
            'phone_number',
            'location',
            'date',
            'is_delivered'
        ]
        widgets = {
            'item': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select item',
            }),
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter customer name',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number',
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter delivery location',
            }),
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'placeholder': 'Select delivery date and time',
                'type': 'datetime-local'
            }),
            'is_delivered': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'label': 'Mark as delivered',
            }),
        }


# forms.py

# forms.py

class FinishedProductForm(forms.ModelForm):
    """
    Formulaire pour ajouter un produit fini.
    """
    class Meta:
        model = Item
        fields = ['name', 'price', 'quantity', 'expiring_date', 'description', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 2
                }
            ),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01'
                }
            ),
            'expiring_date': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local'
                }
            ),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_finished_product'] = forms.BooleanField(
            initial=True,  # Définir la valeur par défaut à True
            widget=forms.HiddenInput()  # Masquer le champ dans le formulaire
        )

from django import forms
from .models import Item

class FinishedProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'quantity', 'price', 'category']  # Uniquement les champs modifiables
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter des informations non modifiables
        self.fields['production_date'] = forms.CharField(
            label="Date de production",
            disabled=True,
            initial=self.instance.fabrications.first().date_created.strftime('%d/%m/%Y') if self.instance.fabrications.exists() else "N/A"
        )
        self.fields['producer'] = forms.CharField(
            label="Producteur",
            disabled=True,
            initial="Optistock"
        )

from django import forms
from .models import ClientOrder  # Cet import doit rester

from django import forms
from .models import ClientOrder

class ClientOrderForm(forms.ModelForm):
    class Meta:
        model = ClientOrder
        fields = ['customer', 'product', 'quantity', 'delivery_date', 'notes']
        widgets = {
            'delivery_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        labels = {
            'customer': 'Client',  # Label en français
            'product': 'Produit',  # Label en français
            'quantity': 'Quantité',  # Label en français
            'delivery_date': 'Date de livraison',  # Label en français
            'notes': 'Remarques',  # Label en français
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer uniquement les produits finis (gardé en anglais)
        self.fields['product'].queryset = self.fields['product'].queryset.filter(is_finished_product=True)
        
        # Ajouter des help_texts en français
        self.fields['quantity'].help_text = 'Entrez la quantité souhaitée'
        self.fields['delivery_date'].help_text = 'Date prévue pour la livraison'
        
        # Validation minimum pour la quantité
        self.fields['quantity'].min_value = 1