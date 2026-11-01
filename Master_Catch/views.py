# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 6

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CatchForm, RegisterForm
from .models import Catch


def home(request):
    return render(request, "Master_Catch/home.html")


def about(request):
    return render(request, "Master_Catch/about.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Master Catch, {user.username}!")
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    # Only ever show the logged-in user's own records.
    records = Catch.objects.filter(owner=request.user).order_by("-length_inches")
    return render(request, "Master_Catch/dashboard.html", {"records": records})


@login_required
def catch_detail(request, pk):
    # Filtering by owner means someone else's record id returns 404, not their data.
    record = get_object_or_404(Catch, pk=pk, owner=request.user)
    return render(request, "Master_Catch/catch_detail.html", {"record": record})


@login_required
def add_catch(request):
    if request.method == "POST":
        form = CatchForm(request.POST, owner=request.user)
        if form.is_valid():
            is_new_species = form.current_record is None
            record = form.save()
            if is_new_species:
                messages.success(request, f"First {record.get_species_display()} logged!")
            else:
                messages.success(request, f"New personal best {record.get_species_display()}!")
            return redirect("catch_detail", pk=record.pk)
    else:
        form = CatchForm(owner=request.user)
    return render(request, "Master_Catch/catch_form.html", {"form": form})


@login_required
@require_POST
def delete_catch(request, pk):
    record = get_object_or_404(Catch, pk=pk, owner=request.user)
    name = record.get_species_display()
    record.delete()
    messages.success(request, f"Your {name} record was deleted.")
    return redirect("dashboard")
