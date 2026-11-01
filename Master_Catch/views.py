# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 6

"""Views (page code) for Master Catch.

Each function gets a web request and returns a page. Every view that
touches records filters by ``owner=request.user`` so users can only
ever see or change their own records.
"""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CatchForm, RegisterForm
from .models import Catch


def home(request):
    """Show the home page (anyone can see it)."""
    return render(request, "Master_Catch/home.html")


def about(request):
    """Show the about page (anyone can see it)."""
    return render(request, "Master_Catch/about.html")


def register(request):
    """Show the sign-up form, create the account, and log the user in."""
    # Already logged in? There is nothing to sign up for.
    if request.user.is_authenticated:
        return redirect("dashboard")
    # POST means the form was submitted.
    if request.method == "POST":
        form = RegisterForm(request.POST)
        # is_valid() checks the username is free and the password rules.
        if form.is_valid():
            user = form.save()
            # Log the new user in so they don't have to log in again.
            login(request, user)
            messages.success(
                request, f"Welcome to Master Catch, {user.username}!"
            )
            return redirect("dashboard")
    else:
        # GET means the page was just opened: show an empty form.
        form = RegisterForm()
    # Show the form (with error messages if the submit failed).
    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    """Show the logged-in user's records, longest fish first."""
    # Only this user's records; "-" means largest first.
    records = Catch.objects.filter(owner=request.user).order_by(
        "-length_inches"
    )
    return render(
        request, "Master_Catch/dashboard.html", {"records": records}
    )


@login_required
def catch_detail(request, pk):
    """Show one record.

    Args:
        request: The web request (request.user is the logged-in user).
        pk: The record's id number from the URL, e.g. /records/5/.
    """
    # Filtering by owner means someone else's id gives a 404 (Not Found)
    # instead of showing their record.
    record = get_object_or_404(Catch, pk=pk, owner=request.user)
    return render(
        request, "Master_Catch/catch_detail.html", {"record": record}
    )


@login_required
def add_catch(request):
    """Show the log-a-catch form and save the fish if it's a new record."""
    if request.method == "POST":
        # Pass the user in so the form checks and saves their records only.
        form = CatchForm(request.POST, owner=request.user)
        # is_valid() also runs the "biggest only" check in CatchForm.clean().
        if form.is_valid():
            # No old record means this is the user's first of this species.
            is_new_species = form.current_record is None
            record = form.save()
            species = record.get_species_display()
            if is_new_species:
                messages.success(request, f"First {species} logged!")
            else:
                messages.success(request, f"New personal best {species}!")
            # Go to the saved record's page.
            return redirect("catch_detail", pk=record.pk)
    else:
        # Page just opened: show an empty form.
        form = CatchForm(owner=request.user)
    return render(request, "Master_Catch/catch_form.html", {"form": form})


@login_required
@require_POST
def delete_catch(request, pk):
    """Delete one of the user's records.

    Only accepts POST (the delete button in the modal), so simply
    visiting the URL can't delete anything.

    Args:
        request: The web request (request.user is the logged-in user).
        pk: The record's id number from the URL.
    """
    # Same owner check as catch_detail: only your own records.
    record = get_object_or_404(Catch, pk=pk, owner=request.user)
    # Save the name before deleting so the message can use it.
    species = record.get_species_display()
    record.delete()
    messages.success(request, f"Your {species} record was deleted.")
    return redirect("dashboard")
