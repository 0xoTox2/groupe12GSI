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