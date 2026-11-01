# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 6

"""Forms for Master Catch: log in, sign up, and log a catch."""

# Django's form tools: Form fields, widgets, ModelForm, ValidationError.
from django import forms
# Django's ready-made login and sign-up forms.
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

# My Catch model, so CatchForm can build its fields from it.
from .models import Catch


class BootstrapFormMixin:
    """Add Bootstrap CSS classes to every field of a form.

    Put this first in a form's parent list so all fields match the site.
    """

    def __init__(self, *args, **kwargs):
        """Build the form normally, then style each field."""
        # Let the real form (login, sign-up or catch) build its fields.
        super().__init__(*args, **kwargs)
        # Go through every field on the form.
        for field in self.fields.values():
            # Dropdowns use Bootstrap's "form-select", other inputs use
            # "form-control".
            if isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    """Django's login form (username and password) with Bootstrap style."""


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    """Django's sign-up form (username, password x2) with Bootstrap style."""


class CatchForm(BootstrapFormMixin, forms.ModelForm):
    """Form to log a catch.

    It only saves if the fish is longer than the user's current record
    for that species. A longer fish replaces the old record.
    """

    class Meta:
        """Which model and fields the form uses."""

        # Build the form from the Catch model.
        model = Catch
        # The fields users fill in. Owner is not on the form: the view
        # passes in the logged-in user and save() sets it.
        fields = [
            "species",
            "length_inches",
            "date_caught",
            "place_caught",
            "notes",
        ]
        # Widgets change how a field is drawn in the HTML.
        widgets = {
            # type="date" shows the browser's calendar picker.
            "date_caught": forms.DateInput(attrs={"type": "date"}),
            # Make the notes box 3 lines tall.
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, owner, **kwargs):
        """Build the form for one user.

        Args:
            owner: The logged-in user the catch belongs to.
        """
        # Build the fields (and the Bootstrap styling from the mixin).
        super().__init__(*args, **kwargs)
        # Remember the user so clean() and save() use only their records.
        self.owner = owner
        # Set in clean(): the user's existing record for the chosen
        # species, or None if this is their first fish of that species.
        self.current_record = None

    def clean(self):
        """Check the "biggest only" rule after the fields are validated.

        Raises:
            ValidationError: If the fish is not longer than the
                user's current record for that species.
        """
        # Run Django's normal checks first and get the cleaned values.
        cleaned = super().clean()
        # .get() returns None if a field failed its own check.
        species = cleaned.get("species")
        length = cleaned.get("length_inches")
        # Only compare if both fields passed their own checks.
        if species and length is not None:
            # Look up this user's record for the species (only theirs).
            # .first() gives the record, or None if there isn't one.
            self.current_record = Catch.objects.filter(
                owner=self.owner, species=species
            ).first()
            # Shorter name to use below.
            record = self.current_record
            # Same length or shorter is not a new record, so stop here.
            if record and length <= record.length_inches:
                # This message shows at the top of the form. %b %d, %Y
                # formats the date like "May 02, 2026".
                raise forms.ValidationError(
                    f"Not a new record. Your best "
                    f"{record.get_species_display()} is "
                    f"{record.length_inches} in, caught "
                    f"{record.date_caught:%b %d, %Y}."
                )
        # Hand the cleaned values back to Django.
        return cleaned

    def save(self, commit=True):
        """Save the catch as the user's record for that species.

        Updates the old record if there is one, otherwise creates a new
        record. Either way the user keeps one record per species.

        Args:
            commit: Save to the database now if True.

        Returns:
            The saved Catch record.
        """
        # Reuse the existing record, or start a new one for this user.
        catch = self.current_record or Catch(owner=self.owner)
        # Copy each form field onto the record (species, length, etc.).
        for name in self.Meta.fields:
            setattr(catch, name, self.cleaned_data[name])
        # Write it to the database (updates the old row or adds a new one).
        if commit:
            catch.save()
        return catch
