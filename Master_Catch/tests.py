# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 6

"""Automated tests for Master Catch.

Run them all with:  python manage.py test

Django builds a brand-new empty test database for every run and deletes
it afterward, so these tests never touch the real db.sqlite3.
"""

# date: build exact catch dates. timedelta: get "tomorrow" for a future date.
from datetime import date, timedelta
# Decimal: compare lengths exactly, the same way the model stores them.
from decimal import Decimal

# Django's built-in User model, to make fake test users.
from django.contrib.auth.models import User
# The error the database raises when the unique constraint is broken.
from django.db import IntegrityError
# TestCase gives each test a fresh database and a fake browser
# (self.client).
from django.test import TestCase
# reverse("name") turns a URL name into its address, e.g. "/records/".
from django.urls import reverse
# timezone.localdate() gives today's date in the site's time zone.
from django.utils import timezone

# My Catch model, to create and check records.
from .models import Catch

# A made-up password used only for the fake test users below.
TEST_PASSWORD = "Test-Only-Pass-123"


def catch_data(species="largemouth_bass", length="20", place="Wilson Lake",
               when="2026-05-02"):
    """Return form data for the Log a Catch form.

    Args:
        species: Saved species value, e.g. "largemouth_bass".
        length: Length in inches as text, like a user would type it.
        place: Where the fish was caught.
        when: Catch date as YYYY-MM-DD text.

    Returns:
        A dict shaped like what the browser sends when the form is
        submitted.
    """
    return {
        "species": species,
        "length_inches": length,
        "date_caught": when,
        "place_caught": place,
        "notes": "",
    }


class BiggestOnlyRuleTests(TestCase):
    """Check the "only the biggest fish of each species counts" rule."""

    def setUp(self):
        """Make a user and log them in before each test."""
        # create_user stores the password hashed, like a real sign up.
        self.user = User.objects.create_user("kyle", password=TEST_PASSWORD)
        # force_login logs in without going through the login page.
        self.client.force_login(self.user)
        # The Log a Catch page address, /records/new/.
        self.url = reverse("add_catch")

    def test_first_catch_is_saved(self):
        """A user's first fish of a species is saved."""
        # Submit the form like a browser would.
        response = self.client.post(self.url, catch_data(length="20"))
        # 302 = the page redirected (to the new record), meaning success.
        self.assertEqual(response.status_code, 302)
        # Exactly one record now exists for this user.
        self.assertEqual(Catch.objects.filter(owner=self.user).count(), 1)

    def test_smaller_fish_is_rejected(self):
        """A shorter fish is not saved and the old record stays."""
        # Set the record at 20 inches, then try an 18 inch fish.
        self.client.post(self.url, catch_data(length="20"))
        response = self.client.post(self.url, catch_data(length="18"))
        # 200 = the form was shown again (with an error) instead of saving.
        self.assertEqual(response.status_code, 200)
        # The page shows the error message.
        self.assertContains(response, "Not a new record")
        # The record is still the 20 inch fish.
        record = Catch.objects.get(owner=self.user)
        self.assertEqual(record.length_inches, Decimal("20"))

    def test_same_length_is_rejected(self):
        """A tie is not a new record."""
        # Two 20 inch fish: the second one must be rejected.
        self.client.post(self.url, catch_data(length="20"))
        response = self.client.post(self.url, catch_data(length="20"))
        self.assertContains(response, "Not a new record")

    def test_bigger_fish_replaces_record(self):
        """A longer fish replaces the old record instead of adding one."""
        # A 20 inch record, then a 24 inch fish from a different lake.
        self.client.post(self.url, catch_data(length="20"))
        self.client.post(
            self.url, catch_data(length="24", place="Cedar Bluff")
        )
        # Still only one largemouth bass record for this user...
        self.assertEqual(Catch.objects.filter(owner=self.user).count(), 1)
        # ...and it now has the new length and place.
        record = Catch.objects.get(owner=self.user)
        self.assertEqual(record.length_inches, Decimal("24"))
        self.assertEqual(record.place_caught, "Cedar Bluff")

    def test_different_species_are_separate(self):
        """Each species has its own record."""
        # A small bluegill still saves because it's a different species.
        self.client.post(self.url, catch_data(species="largemouth_bass"))
        self.client.post(self.url, catch_data(species="bluegill", length="5"))
        # Two records: one per species.
        self.assertEqual(Catch.objects.filter(owner=self.user).count(), 2)

    def test_future_date_is_rejected(self):
        """A catch date after today is not allowed."""
        # Today + 1 day, sent as YYYY-MM-DD text.
        tomorrow = timezone.localdate() + timedelta(days=1)
        response = self.client.post(
            self.url, catch_data(when=tomorrow.isoformat())
        )
        # Form shown again with an error, and nothing was saved.
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Catch.objects.exists())

    def test_users_have_separate_records(self):
        """Another user's smaller fish doesn't touch my record."""
        # My 24 inch record.
        self.client.post(self.url, catch_data(length="24"))
        # Switch the fake browser to a second user.
        other = User.objects.create_user("other", password=TEST_PASSWORD)
        self.client.force_login(other)
        response = self.client.post(self.url, catch_data(length="10"))
        # The other user's first largemouth bass saves fine...
        self.assertEqual(response.status_code, 302)
        # ...and my record is still 24 inches.
        mine = Catch.objects.get(owner=self.user)
        self.assertEqual(mine.length_inches, Decimal("24"))

    def test_database_blocks_duplicate_species(self):
        """The unique constraint stops two records of one species."""
        # Save straight to the database, skipping the form on purpose.
        Catch.objects.create(
            owner=self.user, species="largemouth_bass", length_inches="20",
            date_caught=date(2026, 5, 2), place_caught="Wilson Lake",
        )
        # assertRaises passes only if the code inside raises this error.
        with self.assertRaises(IntegrityError):
            Catch.objects.create(
                owner=self.user, species="largemouth_bass", length_inches="25",
                date_caught=date(2026, 5, 3), place_caught="Wilson Lake",
            )


class AccessControlTests(TestCase):
    """Check that users can only see and change their own records.

    These are the IDOR checks Week 12 attackers will try.
    """

    def setUp(self):
        """Make two users, and one record that belongs to the owner."""
        # The record's owner, and a second user who acts as the attacker.
        self.owner = User.objects.create_user("kyle", password=TEST_PASSWORD)
        self.other = User.objects.create_user("other", password=TEST_PASSWORD)
        # One record owned by "kyle".
        self.record = Catch.objects.create(
            owner=self.owner, species="largemouth_bass", length_inches="24",
            date_caught=date(2026, 5, 2), place_caught="Wilson Lake",
        )
        # Addresses for this record's detail and delete pages.
        self.detail_url = reverse("catch_detail", args=[self.record.pk])
        self.delete_url = reverse("delete_catch", args=[self.record.pk])

    def test_logged_out_user_is_sent_to_login(self):
        """Visitors who aren't logged in can't see record pages."""
        # Check each page that needs a login (no force_login here).
        for url in [reverse("dashboard"), reverse("add_catch"),
                    self.detail_url]:
            # subTest labels each address so a failure says which one.
            with self.subTest(url=url):
                response = self.client.get(url)
                # Expected: sent to /login/?next=<the page they wanted>.
                login_url = f"{reverse('login')}?next={url}"
                self.assertRedirects(response, login_url)

    def test_owner_can_see_record(self):
        """The owner can open their own record."""
        self.client.force_login(self.owner)
        response = self.client.get(self.detail_url)
        # assertContains also checks the page loaded (status 200).
        self.assertContains(response, "Wilson Lake")

    def test_other_user_gets_404_for_record(self):
        """Changing the id in the URL doesn't show someone else's record."""
        # Log in as the other user and open kyle's record address.
        self.client.force_login(self.other)
        response = self.client.get(self.detail_url)
        # 404 = Not Found, so nothing about the record is shown.
        self.assertEqual(response.status_code, 404)

    def test_dashboard_shows_only_own_records(self):
        """My Records never lists another user's fish."""
        self.client.force_login(self.other)
        response = self.client.get(reverse("dashboard"))
        # kyle's record must not appear; the other user has none.
        self.assertNotContains(response, "Wilson Lake")
        self.assertContains(response, "No records yet")

    def test_other_user_cannot_delete_record(self):
        """Another user can't delete my record."""
        self.client.force_login(self.other)
        response = self.client.post(self.delete_url)
        # Not Found, and the record is still in the database.
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Catch.objects.filter(pk=self.record.pk).exists())

    def test_delete_needs_post(self):
        """Just visiting the delete address doesn't delete anything."""
        self.client.force_login(self.owner)
        response = self.client.get(self.delete_url)
        # 405 = "Method Not Allowed" (only POST is accepted).
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Catch.objects.filter(pk=self.record.pk).exists())

    def test_owner_can_delete_record(self):
        """The owner's delete button removes the record."""
        self.client.force_login(self.owner)
        response = self.client.post(self.delete_url)
        # Sent back to My Records, and the record is gone.
        self.assertRedirects(response, reverse("dashboard"))
        self.assertFalse(Catch.objects.filter(pk=self.record.pk).exists())


class AccountTests(TestCase):
    """Check sign up, and that the public pages load."""

    def test_public_pages_load(self):
        """Home, About, Log in and Sign up open for anyone."""
        # Not logged in. Each page should load (200 = OK).
        for name in ["home", "about", "login", "register"]:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_register_creates_user_and_logs_in(self):
        """Signing up makes the account and logs the new user in."""
        # Fill in the sign-up form (password typed twice).
        response = self.client.post(reverse("register"), {
            "username": "newangler",
            "password1": TEST_PASSWORD,
            "password2": TEST_PASSWORD,
        })
        # Sent to My Records, and the account exists.
        self.assertRedirects(response, reverse("dashboard"))
        self.assertTrue(User.objects.filter(username="newangler").exists())
        # The session holds the logged-in user's id after login.
        self.assertIn("_auth_user_id", self.client.session)
