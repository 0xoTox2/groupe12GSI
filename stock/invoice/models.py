from django.db import models
from django_extensions.db.fields import AutoSlugField

from store.models import Item


class Invoice(models.Model):
    """
    Represents an invoice for a purchased item.

    Attributes:
        slug (str): Unique slug based on the date.
        date (datetime): Date of invoice creation.
        customer_name (str): Name of the customer.
        contact_number (str): Customer's contact number.
        item (ForeignKey): The invoiced item.
        price_per_item (float): Price per item.
        quantity (float): Number of items purchased.
        shipping (float): Shipping charges.
        total (float): Total before shipping.
        grand_total (float): Total including shipping.
    """
    status = models.CharField(max_length=20, default='draft')
    slug = AutoSlugField(unique=True, populate_from='date')
    date = models.DateTimeField(
        auto_now=True,
        verbose_name='Date (e.g., 2022/11/22)'
    )
    customer_name = models.CharField(max_length=300,verbose_name='client ')
    contact_number = models.CharField(max_length=13, verbose_name='numéro')
    item = models.ForeignKey(Item, on_delete=models.CASCADE,verbose_name='produit')
    price_per_item = models.FloatField(verbose_name='Prix uniatire ')
    quantity = models.FloatField(default=0.00,verbose_name="Quantité")
    shipping = models.FloatField(verbose_name='livraison ')
    total = models.FloatField(
        verbose_name='prix total ', editable=False
    )
    grand_total = models.FloatField(
        verbose_name='grand total ', editable=False
    )

    def save(self, *args, **kwargs):
        """
        Update total and grand_total before saving.
        """
        self.total = round(self.quantity * self.price_per_item, 2)
        self.grand_total = round(self.total + self.shipping, 2)
        return super().save(*args, **kwargs)

    def __str__(self):
        """
        Return the invoice's slug.
        """
        return self.slug
    
class Meta:
    ordering = ['-date']
