"""
Module: models.py

Contains Django models for handling categories, items, and deliveries.

This module defines the following classes:
- Category: Represents a category for items.
- Item: Represents an item in the inventory.
- Delivery: Represents a delivery of an item to a customer.

Each class provides specific fields and methods for handling related data.
"""

from django.db import models
from django.urls import reverse
from django.forms import model_to_dict
from django_extensions.db.fields import AutoSlugField
from phonenumber_field.modelfields import PhoneNumberField
from accounts.models import Vendor


class Category(models.Model):
    """
    Represents a category for items.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(unique=True, populate_from='name')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        """
        String representation of the category.
        """
        return f"Category: {self.name}"

    class Meta:
        verbose_name_plural = 'Categories'


# models.py

class Item(models.Model):
    """
    Represents an item in the inventory.
    """
    slug = AutoSlugField(unique=True, populate_from='name')
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=256)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    price = models.FloatField(default=0)
    expiring_date = models.DateTimeField(null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    is_finished_product = models.BooleanField(default=False)  # Nouveau champ
    stock_min = models.IntegerField("Stock Minimum", default=5)
    alert_sent = models.BooleanField(default=False)
    location = models.ForeignKey('Warehouse', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.name} - Category: {self.category}, Quantity: {self.quantity}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'slug': self.slug})
    def to_json(self):
        product = model_to_dict(self)
        product['id'] = self.id
        product['text'] = self.name
        product['category'] = self.category.name
        product['quantity'] = 1
        product['total_product'] = 0
        return product

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Items'


class Delivery(models.Model):
    """
    Represents a delivery of an item to a customer.
    """
    item = models.ForeignKey(
        Item, blank=True, null=True, on_delete=models.SET_NULL
    )
    customer_name = models.CharField(max_length=30, blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    location = models.CharField(max_length=20, blank=True, null=True)
    date = models.DateTimeField()
    is_delivered = models.BooleanField(
        default=False, verbose_name='Is Delivered'
    )

    def __str__(self):
        """
        String representation of the delivery.
        """
        return (
            f"Delivery of {self.item} to {self.customer_name} "
            f"at {self.location} on {self.date}"
        )


from django.db import models
from django.urls import reverse

class Nomenclature(models.Model):
    product = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="nomenclatures", verbose_name="Produit fini")
    component = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="used_in_nomenclatures", verbose_name="Matière première")
    quantity = models.PositiveIntegerField(verbose_name="Quantité nécessaire")

    def __str__(self):
        return f"{self.product.name} - {self.component.name} ({self.quantity})"

class Fabrication(models.Model):
    product = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="fabrications", verbose_name="Produit fini")
    quantity = models.PositiveIntegerField(verbose_name="Quantité fabriquée")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    def __str__(self):
        return f"{self.product.name} - {self.quantity} unités (le {self.date_created.strftime('%d/%m/%Y')})"
    
class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()