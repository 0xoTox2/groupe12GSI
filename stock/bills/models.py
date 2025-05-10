from django.db import models
from autoslug import AutoSlugField


class Bill(models.Model):
    """Model representing a bill with various details and payment status."""

    slug = AutoSlugField(unique=True, populate_from='date')
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date (e.g., 2022/11/22)'
    )
    institution_name = models.CharField(
        max_length=30,
        blank=False,
        null=False,
        verbose_name='fournisseur',
        
    )

    phone_number = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='numéro fournisseur'
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Email '
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name= 'Addresse '
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Description de la facture'
    )
    payment_details = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        verbose_name='Details de paiement'
    )
    amount = models.FloatField(
        verbose_name='Prix total',
    )
    status = models.BooleanField(
        default=False,
        verbose_name='Payé',
    )

    def __str__(self):
        return self.institution_name
