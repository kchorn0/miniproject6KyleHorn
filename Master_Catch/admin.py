# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 6

from django.contrib import admin

from .models import Catch

admin.site.site_header = "Master Catch Admin"
admin.site.site_title = "Master Catch Admin"
admin.site.index_title = "Manage personal-best catches"


@admin.register(Catch)
class CatchAdmin(admin.ModelAdmin):
    list_display = ("species", "length_inches", "place_caught", "date_caught", "owner")
    list_display_links = ("species",)
    list_filter = ("species", "date_caught", "owner")
    search_fields = ("place_caught", "notes", "owner__username")
    date_hierarchy = "date_caught"
    ordering = ("species", "-length_inches")
    list_per_page = 25
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("The fish", {"fields": ("owner", "species", "length_inches")}),
        ("Where and when", {"fields": ("place_caught", "date_caught")}),
        ("Notes", {"fields": ("notes",)}),
        ("Record history", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
