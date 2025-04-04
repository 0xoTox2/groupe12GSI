from django import forms
from .models import Purchase
from django.core.validators import MinValueValidator, MaxValueValidator



class BootstrapMixin(forms.ModelForm):
    """
    Un mixin pour ajouter les classes Bootstrap aux champs du formulaire.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class PurchaseForm(BootstrapMixin, forms.ModelForm):
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
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Entrer la quantité'}),
            'delivery_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',  # Utilisez 'date' pour un champ de date uniquement
                'class': 'form-control',
            }),
        }


POLICY_CHOICES = [
    ('fixed', 'Méthode de Réapprovisionnement Fixe'),
    ('point', 'Méthode de Point de Commande'),
    ('replenishment', 'Méthode de Recomplètement'),
    ('degressive', 'Méthode Dégressive'),
    ('degressive_remise', 'Méthode Dégressive avec Remise'), 
]
class PolicySelectionForm(forms.Form):
    policy = forms.ChoiceField(choices=POLICY_CHOICES, label="Choisissez une politique d'approvisionnement")

class FixedReplenishmentForm(forms.Form):
    delai_livraison = forms.IntegerField(label="Délai de livraison (en jours)")
    consommation_annuelle = forms.IntegerField(label="Consommation annuelle (en unités)")
    prix_achat_unitaire = forms.FloatField(label="Prix d’achat unitaire (en DH)")
    taux_possession = forms.FloatField(label="Taux de possession des stocks (en décimal, par exemple 0.08 pour 8%)")
    cout_lancement = forms.FloatField(label="Coût de lancement des commandes (en DH)")

class PointReplenishmentForm(forms.Form):
    stock_actuel = forms.IntegerField(label="Stock actuel (en unités)")
    delai_livraison = forms.IntegerField(label="Délai de livraison (en jours)")
    taille_lot = forms.IntegerField(label="Taille de lot (en unités)")
    consommation_annuelle = forms.IntegerField(label="Consommation annuelle (en unités)")
    prix_achat_unitaire = forms.FloatField(label="Prix d’achat unitaire (en DH)")
    taux_possession = forms.FloatField(label="Taux de possession des stocks (en décimal, par exemple 0.08 pour 8%)")
    cout_lancement = forms.FloatField(label="Coût de lancement des commandes (en DH)")
    stock_securite = forms.FloatField(label="Stock de sécurité (en unités)")

#recompletement
class ReplenishmentForm(forms.Form):
    demande_moyenne = forms.FloatField(label="Demande moyenne par période (D)")
    periode_reapprovisionnement = forms.FloatField(label="Période de réapprovisionnement (T) en jours")
    delai_livraison = forms.FloatField(label="Délai de livraison (L) en jours")
    stock_securite = forms.FloatField(label="Stock de sécurité (Ss)")
    stock_actuel = forms.FloatField(label="Niveau de stock actuel (M)")
    taille_lot = forms.FloatField(label="Taille de lot")

class WagnerWhitinForm(forms.Form):
    n_periodes = forms.IntegerField(label="Nombre de périodes", min_value=1)
    demande = forms.CharField(label="Demande (séparée par des virgules, ex: 10,20,30)", max_length=255)
    cout_commande = forms.FloatField(label="Coût de commande (Cc)")
    cout_possession = forms.FloatField(label="Coût de possession par unité par période (t)")


class WagnerWhitinForm2(forms.Form):
    n_periodes = forms.IntegerField(label="Nombre de périodes", min_value=1)
    demande = forms.CharField(
        label="Demande par période (séparée par des virgules, ex: 10,20,30)", 
        max_length=255
    )
    cout_commande = forms.FloatField(label="Coût de commande (Cc)")
    prix_unitaire = forms.CharField(
        label="Prix unitaire par période (séparés par des virgules, ex: 5,5,6)", 
        max_length=255
    )
    taux_possession = forms.FloatField(label="Taux de possession (en %, ex: 8 pour 8%)")


from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class DegressiveReplenishmentForm(forms.Form):
    consommation_annuelle = forms.IntegerField(
        label="Consommation annuelle (D)",
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    taux_possession = forms.FloatField(
        label="Taux de possession (t%)",
        min_value=0.1,
        max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    cout_commande = forms.FloatField(
        label="Coût de commande (C)",
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    nombre_paliers = forms.IntegerField(
        label="Nombre de paliers",
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'nombre_paliers',
            'onchange': 'updatePaliers()'
        })
    )

from django import forms
# Dans forms.py, ajoutez cette classe (elle existe déjà mais vérifiez qu'elle est bien comme ceci)
class DegressiveRemiseReplenishmentForm(forms.Form):
    consommation_annuelle = forms.IntegerField(
        label="Consommation annuelle (D)",
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    taux_possession = forms.FloatField(
        label="Taux de possession (t%)",
        min_value=0.1,
        max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    cout_commande = forms.FloatField(
        label="Coût de commande (C)",
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    prix_achat_base = forms.FloatField(
        label="Prix d'achat de base (DH)",
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    nombre_paliers = forms.IntegerField(
        label="Nombre de paliers",
        min_value=1,
        max_value=5,
        initial=3,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'nombre_paliers',
            'onchange': 'updatePaliers()'
        })
    )

    def __init__(self, *args, **kwargs):
        nombre_paliers = kwargs.pop('nombre_paliers', 3)
        super().__init__(*args, **kwargs)
        
        for i in range(1, nombre_paliers + 1):
            self.fields[f'remise_{i}'] = forms.FloatField(
                label=f"Remise palier {i} (%)",
                min_value=0,
                max_value=100,
                widget=forms.NumberInput(attrs={
                    'class': 'form-control',
                    'step': '0.1'
                })
            )
            self.fields[f'qmin_{i}'] = forms.IntegerField(
                label=f"Quantité minimale palier {i}",
                min_value=0,
                widget=forms.NumberInput(attrs={'class': 'form-control'})
            )
            self.fields[f'qmax_{i}'] = forms.IntegerField(
                label=f"Quantité maximale palier {i}",
                min_value=1,
                widget=forms.NumberInput(attrs={'class': 'form-control'})
            )