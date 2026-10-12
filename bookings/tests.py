from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from bookings.models import Booking, PromotionalOffer
from cars.models import Car, CarCategory


class AuthTests(TestCase):
    def test_register_login(self):
        resp = self.client.post(reverse("accounts:register"), {
            "username": "testuser", "email": "t@example.com", "full_name": "Test User",
            "mobile_number": "+919999999999", "password1": "StrongPass123!", "password2": "StrongPass123!",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(User.objects.filter(username="testuser").exists())
        self.client.logout()
        self.assertTrue(self.client.login(username="testuser", password="StrongPass123!"))

    def test_duplicate_email_blocked(self):
        User.objects.create_user("u1", email="dup@example.com", password="x")
        resp = self.client.post(reverse("accounts:register"), {
            "username": "u2", "email": "dup@example.com", "full_name": "U2",
            "mobile_number": "+919999999998", "password1": "StrongPass123!", "password2": "StrongPass123!",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "already exists")


class PricingBookingTests(TestCase):
    def setUp(self):
        self.cat = CarCategory.objects.create(name="regular")
        self.car = Car.objects.create(brand="Tata", model="Nexon", category=self.cat, transmission="manual", fuel_type="petrol", seating_capacity=5, daily_price=2000)
        self.user = User.objects.create_user("renter", password="StrongPass123!")
        self.offer = PromotionalOffer.objects.create(
            title="Test", description="d", promo_code="TEST10", min_days=2, discount_percent=10,
            max_discount=1000, valid_from=timezone.now().date() - timedelta(days=1),
            valid_to=timezone.now().date() + timedelta(days=30), is_active=True)

    def test_compute_days_ceiling(self):
        p = timezone.now() + timedelta(hours=1)
        r = p + timedelta(hours=25)
        self.assertEqual(Booking.compute_days(p, r), 2)

    def test_overlap_blocked(self):
        p = timezone.now() + timedelta(days=1)
        r = p + timedelta(days=2)
        Booking.objects.create(user=self.user, car=self.car, pickup_datetime=p, return_datetime=r, status="confirmed")
        b2 = Booking(user=self.user, car=self.car, pickup_datetime=p + timedelta(hours=1), return_datetime=r + timedelta(hours=1))
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            b2.full_clean()

    def test_offer_applied(self):
        p = timezone.now() + timedelta(days=1)
        r = p + timedelta(days=3)
        b = Booking(user=self.user, car=self.car, pickup_datetime=p, return_datetime=r, offer=self.offer)
        days, base, disc, total = b.calculate_amounts()
        self.assertEqual(days, 3)
        self.assertEqual(base, Decimal("6000.00"))
        self.assertEqual(disc, Decimal("600.00"))
        self.assertEqual(total, Decimal("5400.00"))

    def test_permissions(self):
        other = User.objects.create_user("other", password="x")
        p = timezone.now() + timedelta(days=1)
        r = p + timedelta(days=2)
        b = Booking.objects.create(user=self.user, car=self.car, pickup_datetime=p, return_datetime=r)
        self.client.login(username="other", password="x")
        resp = self.client.get(reverse("bookings:confirmation", args=[b.reference]))
        self.assertEqual(resp.status_code, 404)
