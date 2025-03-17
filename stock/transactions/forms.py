from django import forms
from .models import Purchase


class BootstrapMixin(forms.ModelForm):
    """
    Un mixin pour ajouter les classes Bootstrap aux champs du formulaire.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class PurchaseForm(BootstrapMixin, forms.ModelForm):
    """
    Formulaire pour créer et mettre à jour des achats.
    """
    class Meta:
        model = Purchase
        fields = [
            'item', 'price', 'description', 'vendor',
            'quantity', 'delivery_date', 'delivery_status'
        ]
        labels = {
            'item': 'Article',
            'price': 'Prix',
            'description': 'Description',
            'vendor': 'Fournisseur',
            'quantity': 'Quantité',
            'delivery_date': 'Date de livraison',
            'delivery_status': 'Statut de livraison',
        }
        widgets = {
            'delivery_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local'
                }
            ),
            'description': forms.Textarea(
                attrs={'rows': 1, 'cols': 40, 'class': 'form-control', 'placeholder': 'Ajouter une description'}
            ),
            'quantity': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Entrer la quantité'}
            ),
            'delivery_status': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'price': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Entrer le prix'}
            ),
        }
