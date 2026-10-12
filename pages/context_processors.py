from django.conf import settings


def site_config(request):
    return {
        "COMPANY_NAME": getattr(settings, "COMPANY_NAME", "TopGear Self-Drive Cars"),
        "COMPANY_PHONE": getattr(settings, "COMPANY_PHONE", ""),
        "COMPANY_PHONE_TEL": getattr(settings, "COMPANY_PHONE_TEL", ""),
        "COMPANY_EMAIL": getattr(settings, "COMPANY_EMAIL", ""),
        "COMPANY_CITY": getattr(settings, "COMPANY_CITY", "Hyderabad"),
        "PAYMENT_POLICY_LABEL": getattr(settings, "PAYMENT_POLICY_LABEL", ""),
    }
