from django.db import models
from django_extensions.db.fields import AutoSlugField

from store.models import Item
from accounts.models import Vendor, Customer

DELIVERY_CHOICES = [("P", "Pending"), ("S", "Successful")]


class Sale(models.Model):
    """
    Represents a sale transaction involving a customer.
    """

    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Sale Date"
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.DO_NOTHING,
        db_column="customer"
    )
    sub_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0
    )
    grand_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0
    )
    tax_percentage = models.FloatField(default=0.0)
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0
    )
    amount_change = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0
    )

    class Meta:
        db_table = "sales"
        verbose_name = "Sale"
        verbose_name_plural = "Sales"

    def __str__(self):
        """
        Returns a string representation of the Sale instance.
        """
        return (
            f"Sale ID: {self.id} | "
            f"Grand Total: {self.grand_total} | "
            f"Date: {self.date_added}"
        )

    def sum_products(self):
        """
        Returns the total quantity of products in the sale.
        """
        return sum(detail.quantity for detail in self.saledetail_set.all())


class SaleDetail(models.Model):
    """
    Represents details of a specific sale, including item and quantity.
    """

    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        db_column="sale",
        related_name="saledetail_set"
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.DO_NOTHING,
        db_column="item"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    quantity = models.PositiveIntegerField()
    total_detail = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "sale_details"
        verbose_name = "Sale Detail"
        verbose_name_plural = "Sale Details"

    def __str__(self):
        """
        Returns a string representation of the SaleDetail instance.
        """
        return (
            f"Detail ID: {self.id} | "
            f"Sale ID: {self.sale.id} | "
            f"Quantity: {self.quantity}"
        )




class Purchase(models.Model):
    # Champs existants
    slug = models.SlugField(unique=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    description = models.TextField(max_length=300, blank=True, null=True)
    vendor = models.ForeignKey(Vendor, related_name="purchases", on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(blank=True, null=True, verbose_name="Date de livraison")
    quantity = models.PositiveIntegerField(default=0)
    delivery_status = models.CharField(max_length=1, choices=DELIVERY_CHOICES, default="P", verbose_name="Delivery Status")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Price per item (Ksh)")
    total_value = models.DecimalField(max_digits=10, decimal_places=2)

    # Nouveaux champs pour stocker les informations sur la politique
    policy_used = models.CharField(max_length=50, blank=True, null=True, verbose_name="Politique utilisée")
    policy_parameters = models.JSONField(blank=True, null=True, verbose_name="Paramètres de la politique")

    def __str__(self):
        return str(self.item.name)

    class Meta:
        ordering = ["order_date"]

from django.db import models
from decimal import Decimal  # Ajoutez cette importation en haut du fichier
from math import sqrt

class ReapprovisionnementFixe(models.Model):
    delai_livraison = models.IntegerField(verbose_name="Délai de livraison (en jours)")
    consommation_annuelle = models.IntegerField(verbose_name="Consommation annuelle (en unités)")
    prix_achat_unitaire = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix d’achat unitaire (en DH)")
    taux_possession = models.FloatField(verbose_name="Taux de possession des stocks (en décimal, par exemple 0.08 pour 8%)")
    cout_lancement = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Coût de lancement des commandes (en DH)")

    def calculer_qec(self):
        # Convertir les valeurs en Decimal avant de faire les calculs
        consommation_annuelle = Decimal(self.consommation_annuelle)
        cout_lancement = Decimal(self.cout_lancement)
        prix_achat_unitaire = Decimal(self.prix_achat_unitaire)
        taux_possession = Decimal(str(self.taux_possession))  # Convertir float en Decimal via str

        # Calcul de la Quantité Économique de Commande (QEC)
        qec = sqrt((2 * consommation_annuelle * cout_lancement) / (prix_achat_unitaire * taux_possession))
        return qec

    def calculer_periode_reapprovisionnement(self):
        qec = self.calculer_qec()
        consommation_annuelle = Decimal(self.consommation_annuelle)
        periode = (qec / consommation_annuelle) * Decimal('365')  # Convertir 365 en Decimal
        return periode

    def calculer_cout_lancement(self):
        qec = self.calculer_qec()
        consommation_annuelle = Decimal(self.consommation_annuelle)
        cout_lancement = Decimal(self.cout_lancement)
        return (consommation_annuelle / qec) * cout_lancement

    def calculer_cout_possession(self):
        qec = self.calculer_qec()
        prix_achat_unitaire = Decimal(self.prix_achat_unitaire)
        taux_possession = Decimal(str(self.taux_possession))  # Convertir float en Decimal via str
        return (qec / Decimal('2')) * prix_achat_unitaire * taux_possession

    def calculer_cout_total_stock(self):
        cout_lancement = self.calculer_cout_lancement()
        cout_possession = self.calculer_cout_possession()
        return cout_lancement + cout_possession