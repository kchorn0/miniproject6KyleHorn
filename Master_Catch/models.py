# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 6

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


def not_in_future(value):
    if value > timezone.localdate():
        raise ValidationError("The catch date can't be in the future.")


class Catch(models.Model):
    """A user's personal-best (longest) fish for one species."""

    SPECIES_CHOICES = [
        ("largemouth_bass", "Largemouth Bass"),
        ("smallmouth_bass", "Smallmouth Bass"),
        ("white_bass", "White Bass"),
        ("striped_bass", "Striped Bass"),
        ("wiper", "Wiper"),
        ("walleye", "Walleye"),
        ("saugeye", "Saugeye"),
        ("crappie", "Crappie"),
        ("bluegill", "Bluegill"),
        ("channel_catfish", "Channel Catfish"),
        ("blue_catfish", "Blue Catfish"),
        ("flathead_catfish", "Flathead Catfish"),
        ("northern_pike", "Northern Pike"),
        ("rainbow_trout", "Rainbow Trout"),
        ("common_carp", "Common Carp"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="catches",
    )
    species = models.CharField(max_length=30, choices=SPECIES_CHOICES)
    length_inches = models.DecimalField(
        "length (inches)",
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.25")),
            MaxValueValidator(Decimal("150")),
        ],
    )
    date_caught = models.DateField(validators=[not_in_future])
    place_caught = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "catches"
        ordering = ["species"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "species"],
                name="one_record_per_species_per_user",
            ),
        ]

    def __str__(self):
        return f"{self.get_species_display()} - {self.length_inches} in ({self.owner})"
