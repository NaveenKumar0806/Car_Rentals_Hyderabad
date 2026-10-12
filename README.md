# TopGear — Self-Drive Cars (Hyderabad)

Django + Bootstrap 5 self-drive car rental platform.

## Quick start (Windows / PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # optional; settings read env with safe defaults
python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser   # admin login at /admin/
python manage.py runserver
```

Open http://127.0.0.1:8000/

## User journey
Register → Login → Browse Cars → Search/Filter → View Details → Select dates → Price estimate → Submit → Confirmation → Manage in Profile/Dashboard.

## Admin
- Route: `/admin/` (staff/superuser only; never hardcode credentials).
- Manage cars (price, availability, images), bookings (confirm/cancel), customers, offers (codes, validity, caps).

## Notes
- Bookings are labelled **Payment on pickup / Awaiting payment**; never marked Paid without a real payment provider.
- Overlaps of pending/confirmed bookings for the same car are blocked.
- Rental days = ceiling of hours/24, minimum 1.
- Company phone/email come from settings/env and `pages` context processor.
- Tests: `python manage.py test`
hello bye