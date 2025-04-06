from django.db import models
from django.contrib.auth.models import User
from django_extensions.db.fields import AutoSlugField
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from phonenumber_field.modelfields import PhoneNumberField

# Define choices for profile status and roles
STATUS_CHOICES = [
    ('INA', 'Inactif'),
    ('A', 'Actif'),
    ('OL', 'En congé')
]

ROLE_CHOICES = [
    ('RGS', 'Responsable Gestion Stock'),
    ('RPA', 'Responsable Production/Approvisionnement'),
    ('MAG', 'Magasinier')
]

class Profile(models.Model):
    """
    Représente un profil utilisateur contenant des informations personnelles et liées au compte.
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name='Utilisateur'
    )
    slug = AutoSlugField(
        unique=True,
        verbose_name='ID du compte',
        populate_from='email'
    )
    profile_picture = ProcessedImageField(
        default='profile_pics/default.jpg',
        upload_to='profile_pics',
        format='JPEG',
        processors=[ResizeToFill(150, 150)],
        options={'quality': 100}
    )
    telephone = PhoneNumberField(
        null=True, blank=True, verbose_name='Téléphone'
    )
    email = models.EmailField(
        max_length=150, blank=True, null=True, verbose_name='Email'
    )
    first_name = models.CharField(
        max_length=30, blank=True, verbose_name='Prénom'
    )
    last_name = models.CharField(
        max_length=30, blank=True, verbose_name='Nom de famille'
    )
    status = models.CharField(
        choices=STATUS_CHOICES,
        max_length=12,
        default='INA',
        verbose_name='Statut'
    )
    role = models.CharField(
        choices=ROLE_CHOICES,
        max_length=12,
        blank=True,
        null=True,
        verbose_name='Rôle'
    )

    @property
    def image_url(self):
        """
        Retourne l'URL de l'image de profil.
        Retourne une chaîne vide si l'image n'est pas disponible.
        """
        try:
            return self.profile_picture.url
        except AttributeError:
            return ''

    def __str__(self):
        """
        Retourne une représentation en chaîne du profil.
        """
        return f"Profil de {self.user.username}"

    class Meta:
        """Options Meta pour le modèle Profile."""
        ordering = ['slug']
        verbose_name = 'Profil'
        verbose_name_plural = 'Profiles'

class Vendor(models.Model):
    """
    Represents a vendor with contact and address information.
    """
    name = models.CharField(max_length=50, verbose_name='Name')
    slug = AutoSlugField(
        unique=True,
        populate_from='name',
        verbose_name='Slug'
    )
    phone_number = models.BigIntegerField(
        blank=True, null=True, verbose_name='Phone Number'
    )
    address = models.CharField(
        max_length=50, blank=True, null=True, verbose_name='Address'
    )

    def __str__(self):
        """
        Returns a string representation of the vendor.
        """
        return self.name

    class Meta:
        """Meta options for the Vendor model."""
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'


class Customer(models.Model):
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256, blank=True, null=True)
    address = models.TextField(max_length=256, blank=True, null=True)
    email = models.EmailField(max_length=256, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    loyalty_points = models.IntegerField(default=0)
    last_purchase = models.DateTimeField(null=True)
    preferred_categories = models.ManyToManyField('store.Category')
    class Meta:
        db_table = 'Customers'

    def __str__(self) -> str:
        return self.first_name + " " + self.last_name

    def get_full_name(self):
        return self.first_name + " " + self.last_name

    def to_select2(self):
        item = {
            "label": self.get_full_name(),
            "value": self.id
        }
        return item


class SalesTeam(models.Model):
    ROLES = [
        ('CM', 'Commercial'),
        ('SM', 'Sales Manager'),
        ('AM', 'Account Manager')
    ]

    name = models.CharField("Nom complet", max_length=100)
    role = models.CharField("Rôle", max_length=2, choices=ROLES, default='CM')
    zone = models.CharField("Zone géographique", max_length=50)
    sales_goal = models.DecimalField("Objectif mensuel (DH)", max_digits=10, decimal_places=2)
    achieved = models.DecimalField("Objectif Réalisé (DH)", max_digits=10, decimal_places=2, default=0)

    @property
    def achievement_rate(self):
        return round((self.achieved / self.sales_goal * 100) if self.sales_goal else 0, 2)

    def __str__(self):
        return f"{self.name} - {self.get_role_display()}"