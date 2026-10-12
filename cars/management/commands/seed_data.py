from datetime import date, timedelta

from django.core.management.base import BaseCommand

from bookings.models import PromotionalOffer
from cars.models import Car, CarCategory


class Command(BaseCommand):
    help = "Seed demo categories, cars and offers."

    def handle(self, *args, **options):
        regular, _ = CarCategory.objects.get_or_create(name="regular", defaults={"description": "Everyday hatchbacks, sedans & SUVs."})
        luxury, _ = CarCategory.objects.get_or_create(name="luxury", defaults={"description": "Premium & luxury vehicles."})

        regular_cars = [
            ("Maruti Suzuki", "Swift", "manual", "petrol", 5, 2000),
            ("Maruti Suzuki", "Swift Dzire", "manual", "petrol", 5, 2000),
            ("Maruti Suzuki", "Ertiga", "manual", "petrol", 7, 2000),
            ("Maruti Suzuki", "Brezza", "manual", "diesel", 5, 2000),
            ("Tata", "Nexon", "manual", "petrol", 5, 2000),
            ("Tata", "Altroz", "manual", "petrol", 5, 2000),
            ("Volkswagen", "Polo GT", "automatic", "petrol", 5, 2000),
            ("Hyundai", "i20", "manual", "petrol", 5, 2000),
            ("Hyundai", "i10", "manual", "petrol", 5, 2000),
            ("Tata", "Punch", "manual", "petrol", 5, 2000),
            ("Hyundai", "Aura", "manual", "petrol", 5, 2000),
            ("Toyota", "Innova", "manual", "diesel", 7, 2000),
            ("Toyota", "Glanza", "manual", "petrol", 5, 2000),
            ("Maruti Suzuki", "Baleno", "automatic", "petrol", 5, 2000),
        ]
        for i, (brand, model, trans, fuel, seats, price) in enumerate(regular_cars):
            Car.objects.get_or_create(
                brand=brand, model=model,
                defaults={
                    "category": regular, "transmission": trans, "fuel_type": fuel,
                    "seating_capacity": seats, "daily_price": price,
                    "is_popular": i < 6,
                    "features": "Air conditioning, Power steering, Bluetooth, Airbags, Reverse camera",
                    "rental_terms": "Valid licence required. 250 km/day included; excess billed extra.",
                    "image_url": f"https://images.unsplash.com/photo-1502877338535-766e1452684a?auto=format&fit=crop&w=800&q=60&sig={i}",
                },
            )

        luxury_demo = [
            ("Mercedes-Benz", "C-Class", "automatic", "petrol", 5, 8500),
            ("BMW", "3 Series", "automatic", "diesel", 5, 9000),
            ("Audi", "A4", "automatic", "petrol", 5, 8800),
            ("Jaguar", "XF", "automatic", "diesel", 5, 11000),
            ("Range Rover", "Evoque", "automatic", "diesel", 5, 14000),
            ("Mercedes-Benz", "GLC", "automatic", "diesel", 5, 12500),
        ]
        for i, (brand, model, trans, fuel, seats, price) in enumerate(luxury_demo):
            Car.objects.get_or_create(
                brand=brand, model=model,
                defaults={
                    "category": luxury, "transmission": trans, "fuel_type": fuel,
                    "seating_capacity": seats, "daily_price": price, "is_popular": i < 2,
                    "features": "Leather seats, Cruise control, Premium audio, Navigation, Parking sensors",
                    "rental_terms": "Premium security deposit applies. Chauffeur option on request.",
                    "image_url": f"https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=800&q=60&sig={i}",
                },
            )

        today = date.today()
        offers = [
            ("3+2 Free — Extra Days", "Book for 3 days and get 2 additional days free (equivalent discount).", "TOPGEAR32", 3, 40, 4000, "both"),
            ("Weekend Getaway", "Flat weekend discount on 2+ day rentals.", "WEEKEND15", 2, 15, 2000, "both"),
            ("Multi-Day Saver", "Save more on week-long trips.", "WEEK10", 7, 10, 5000, "both"),
            ("Holiday Package", "Limited-time festive offer.", "HOLIDAY20", 2, 20, 3000, "both"),
        ]
        for title, desc, code, mindays, pct, cap, cats in offers:
            PromotionalOffer.objects.get_or_create(
                promo_code=code,
                defaults={"title": title, "description": desc, "min_days": mindays,
                          "discount_percent": pct, "max_discount": cap,
                          "valid_from": today - timedelta(days=1), "valid_to": today + timedelta(days=180),
                          "applicable_categories": cats, "is_active": True},
            )
        self.stdout.write(self.style.SUCCESS("Seeded categories, cars and offers."))
