# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 6

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Catch


class BootstrapFormMixin:
    """Adds Bootstrap classes to every field so the forms match the site."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            field.widget.attrs["class"] = css


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    pass


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    pass


class CatchForm(BootstrapFormMixin, forms.ModelForm):
    """Log a catch. It only saves if it beats the user's record for that species."""

    class Meta:
        model = Catch
        fields = ["species", "length_inches", "date_caught", "place_caught", "notes"]
        widgets = {
            "date_caught": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, owner, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = owner
        self.current_record = None

    def clean(self):
        cleaned = super().clean()
        species = cleaned.get("species")
        length = cleaned.get("length_inches")
        if species and length is not None:
            self.current_record = Catch.objects.filter(owner=self.owner, species=species).first()
            record = self.current_record
            if record and length <= record.length_inches:
                raise forms.ValidationError(
                    f"Not a new record. Your best {record.get_species_display()} is "
                    f"{record.length_inches} in, caught {record.date_caught:%b %d, %Y}."
                )
        return cleaned

    def save(self, commit=True):
        """Replace the old record for this species, or create the first one."""
        catch = self.current_record or Catch(owner=self.owner)
        for name in self.Meta.fields:
            setattr(catch, name, self.cleaned_data[name])
        if commit:
            catch.save()
        return catch
