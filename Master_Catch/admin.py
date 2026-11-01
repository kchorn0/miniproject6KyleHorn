# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 6

"""Django admin setup for Master Catch.

Registers the ``Catch`` model and styles its list and edit pages so
records are easy to find, read and enter.
"""

from django.contrib import admin

from .models import Catch

# Titles shown at the top of the admin and in the browser tab.
admin.site.site_header = "Master Catch Admin"
admin.site.site_title = "Master Catch Admin"
admin.site.index_title = "Manage personal-best catches"


# @admin.register adds the Catch model to the admin using these options.
@admin.register(Catch)
class CatchAdmin(admin.ModelAdmin):
    """How catches look and behave in the admin."""

    # Columns in the list of catches.
    list_display = (
        "species",
        "length_inches",
        "place_caught",
        "date_caught",
        "owner",
    )
    # Clicking the species opens that catch for editing.
    list_display_links = ("species",)
    # Filter boxes on the right side of the list.
    list_filter = ("species", "date_caught", "owner")
    # Fields the search box looks in (owner__username = the owner's name).
    search_fields = ("place_caught", "notes", "owner__username")
    # Year > month > day links above the list to browse by catch date.
    date_hierarchy = "date_caught"
    # Sort by species, then longest fish first.
    ordering = ("species", "-length_inches")
    # Show 25 catches per page.
    list_per_page = 25
    # Timestamps are set automatically, so show them but don't allow edits.
    readonly_fields = ("created_at", "updated_at")
    # Groups the edit form into titled sections.
    fieldsets = (
        ("The fish", {"fields": ("owner", "species", "length_inches")}),
        ("Where and when", {"fields": ("place_caught", "date_caught")}),
        ("Notes", {"fields": ("notes",)}),
        # "collapse" hides this section until you click "Show".
        ("Record history", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
