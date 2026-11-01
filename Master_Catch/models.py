# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 6

"""Database models for Master Catch.

There is one model, ``Catch``. Each row is a user's personal best
(longest fish) for one species.
"""

# Decimal gives exact numbers for lengths like 21.50 (floats can round).
from decimal import Decimal

# settings.AUTH_USER_MODEL points to Django's built-in User model.
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


def not_in_future(value):
    """Reject a catch date that is later than today.

    Django runs this when a form checks the ``date_caught`` field.
    """
    # localdate() is today's date in the site's time zone (Central).
    if value > timezone.localdate():
        raise ValidationError("The catch date can't be in the future.")


class Catch(models.Model):
    """A user's personal-best (longest) fish for one species."""

    # Choices for the species dropdown. The left value is saved in the
    # database, the right value is what users see on the page.
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

    # The user who caught the fish. Deleting a user deletes their records.
    # related_name lets me write user.catches.all() to get a user's records.
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="catches",
    )
    # Picked from the dropdown above, so spelling is always the same.
    species = models.CharField(max_length=30, choices=SPECIES_CHOICES)
    # Up to 999.99 inches is possible in the database, but the validators
    # only allow 0.25 to 150 inches.
    length_inches = models.DecimalField(
        "length (inches)",
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.25")),
            MaxValueValidator(Decimal("150")),
        ],
    )
    # The day the fish was caught. Can't be a future date.
    date_caught = models.DateField(validators=[not_in_future])
    # Lake, river or pond name, e.g. "Wilson Lake".
    place_caught = models.CharField(max_length=100)
    # Optional extra info like bait or weather. blank=True makes it optional.
    notes = models.TextField(blank=True)
    # Filled in automatically: when the row was first made, and last changed.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Extra settings for the Catch table."""

        # The admin shows "catches" instead of the default "catchs".
        verbose_name_plural = "catches"
        # Default sort order: alphabetical by species.
        ordering = ["species"]
        # The database itself refuses a second row with the same owner
        # and species, so each user has only one record per species.
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "species"],
                name="one_record_per_species_per_user",
            ),
        ]

    def __str__(self):
        """Return a readable label, e.g. 'Walleye - 24.00 in (kyle)'."""
        return (
            f"{self.get_species_display()} - "
            f"{self.length_inches} in ({self.owner})"
        )
