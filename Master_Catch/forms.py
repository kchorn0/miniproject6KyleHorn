# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 6

"""Forms for Master Catch: log in, sign up, and log a catch."""

from django import forms
# Django's ready-made login and sign-up forms.
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Catch


class BootstrapFormMixin:
    """Add Bootstrap CSS classes to every field of a form.

    Put this first in a form's parent list so all fields match the site.
    """

    def __init__(self, *args, **kwargs):
        """Build the form normally, then style each field."""
        super().__init__(*args, **kwargs)
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

        model = Catch
        # Owner is not on the form; the view sets it to the logged-in user.
        fields = [
            "species",
            "length_inches",
            "date_caught",
            "place_caught",
            "notes",
        ]
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
        super().__init__(*args, **kwargs)
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
        cleaned = super().clean()
        species = cleaned.get("species")
        length = cleaned.get("length_inches")
        # Only compare if both fields passed their own checks.
        if species and length is not None:
            # Look up this user's record for the species (only theirs).
            self.current_record = Catch.objects.filter(
                owner=self.owner, species=species
            ).first()
            record = self.current_record
            # Same length or shorter is not a new record, so stop here.
            if record and length <= record.length_inches:
                raise forms.ValidationError(
                    f"Not a new record. Your best "
                    f"{record.get_species_display()} is "
                    f"{record.length_inches} in, caught "
                    f"{record.date_caught:%b %d, %Y}."
                )
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
        if commit:
            catch.save()
        return catch
