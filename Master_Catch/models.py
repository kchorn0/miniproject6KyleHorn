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
# The error a validator raises to show a message on the form.
from django.core.exceptions import ValidationError
# Ready-made checks for the smallest and largest allowed length.
from django.core.validators import MaxValueValidator, MinValueValidator
# Field types (CharField, DateField...) and the Model base class.
from django.db import models
# timezone.localdate() gives today's date in the site's time zone.
from django.utils import timezone


def not_in_future(value):
    """Reject a catch date that is later than today.

    Django runs this when the Log a Catch form (or the admin form)
    validates ``date_caught``. A plain ``save()`` in code skips it.

    Args:
        value: The date entered for ``date_caught``.

    Raises:
        ValidationError: If the date is after today.
    """
    # localdate() is today's date in the site's time zone (Central).
    if value > timezone.localdate():
        raise ValidationError("The catch date can't be in the future.")


class Catch(models.Model):
    """A user's personal-best (longest) fish for one species."""

    # Choices for the species dropdown, in alphabetical order by the name
    # users see. The left value is saved in the database, the right value
    # is what users see on the page.
    SPECIES_CHOICES = [
        ("barracuda", "Barracuda"),
        ("largemouth_bass", "Bass, Largemouth"),
        ("peacock_bass", "Bass, Peacock"),
        ("rock_bass", "Bass, Rock"),
        ("sea_bass", "Bass, Sea"),
        ("smallmouth_bass", "Bass, Smallmouth"),
        ("striped_bass", "Bass, Striped"),
        ("white_bass", "Bass, White"),
        ("bluefish", "Bluefish"),
        ("bluegill", "Bluegill (Bream, Brim)"),
        ("bonefish", "Bonefish"),
        ("bowfin", "Bowfin"),
        ("common_carp", "Carp"),
        ("blue_catfish", "Catfish, Blue"),
        ("bullhead_catfish", "Catfish, Bullhead (Brown, Yellow & Black)"),
        ("channel_catfish", "Catfish, Channel"),
        ("flathead_catfish", "Catfish, Flathead"),
        ("black_crappie", "Crappie (Black)"),
        ("white_crappie", "Crappie (White)"),
        ("grayling", "Grayling"),
        ("jack_crevalle", "Jack Crevalle"),
        ("mackerel", "Mackerel"),
        ("musky", "Musky"),
        ("white_perch", "Perch, White"),
        ("yellow_perch", "Perch, Yellow"),
        ("pickerel", "Pickerel"),
        ("northern_pike", "Pike, Northern"),
        ("redfish", "Redfish"),
        ("atlantic_salmon", "Salmon, Atlantic"),
        ("chinook_salmon", "Salmon, Chinook (King)"),
        ("chum_salmon", "Salmon, Chum"),
        ("coho_salmon", "Salmon, Coho (Silver)"),
        ("kokanee_salmon", "Salmon, Kokanee"),
        ("pink_salmon", "Salmon, Pink"),
        ("quananiche_salmon", "Salmon, Quananiche (Landlocked)"),
        ("sockeye_salmon", "Salmon, Sockeye (Red)"),
        ("saugeye", "Saugeye"),
        ("snakehead", "Snakehead"),
        ("snook", "Snook"),
        ("steelhead", "Steelhead"),
        ("shellcracker", "Sunfish (Shellcracker)"),
        ("brook_trout", "Trout, Brook"),
        ("brown_trout", "Trout, Brown"),
        ("cutthroat_trout", "Trout, Cutthroat"),
        ("dolly_varden_trout", "Trout, Dolly Varden"),
        ("lake_trout", "Trout, Lake"),
        ("palomino_trout", "Trout, Palomino"),
        ("rainbow_trout", "Trout, Rainbow"),
        ("sea_trout", "Trout, Sea/Speckled"),
        ("walleye", "Walleye"),
        ("wiper", "Wiper"),
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
    # "length (inches)" is the label shown on forms. 5 digits with 2 after
    # the decimal point fits up to 999.99, but the validators only allow
    # 0.25 to 150 inches.
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
        # Default sort order: A to Z by the saved species value
        # (e.g. "barracuda", "black_crappie", "blue_catfish"...).
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
        """Return a label, e.g. 'Bass, Largemouth - 24.00 in (kyle)'."""
        return (
            f"{self.get_species_display()} - "
            f"{self.length_inches} in ({self.owner})"
        )
