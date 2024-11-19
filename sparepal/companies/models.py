# Create your models here.
from django.contrib.auth import get_user_model
from django.db import models

# Selection options (Assumed)
LEGAL_STATUS_CHOICES = [
    ("Sole Proprietorship", "Sole Proprietorship"),
    ("Partnership", "Partnership"),
    ("Limited Liability Supplier", "Limited Liability Supplier"),
    ("Corporation", "Corporation"),
]

BUSINESS_DESCRIPTION_CHOICES = [
    ("Retailer", "Retailer"),
    ("Wholesaler", "Wholesaler"),
    ("Distributor", "Distributor"),
    ("Manufacturer", "Manufacturer"),
]

SUB_GROUP_DESCRIPTION_CHOICES = [
    ("Automotive Parts", "Automotive Parts"),
    ("Electronics", "Electronics"),
    ("Machinery", "Machinery"),
    ("Tools", "Tools"),
]

REGION_CHOICES = [
    ("Addis Ababa", "Addis Ababa"),
    ("Oromia", "Oromia"),
    ("Amhara", "Amhara"),
    ("Tigray", "Tigray"),
]

ZONE_CHOICES = [
    ("Central", "Central"),
    ("East", "East"),
    ("West", "West"),
]

WOREDA_CHOICES = [
    ("Woreda 1", "Woreda 1"),
    ("Woreda 2", "Woreda 2"),
    ("Woreda 3", "Woreda 3"),
]

SITE_ID_CHOICES = [
    ("Site A", "Site A"),
    ("Site B", "Site B"),
    ("Site C", "Site C"),
]

# Models


class Company(models.Model):
    company_name = models.CharField(max_length=255)
    date_registered = models.DateField()
    tin_number = models.CharField(max_length=20)
    renewed_license_date = models.DateField()
    license_number = models.CharField(max_length=100)
    legal_status = models.CharField(max_length=50, choices=LEGAL_STATUS_CHOICES)
    code = models.CharField(max_length=50)
    business_description = models.CharField(
        max_length=100,
        choices=BUSINESS_DESCRIPTION_CHOICES,
    )
    sub_group_code = models.CharField(max_length=50)
    sub_group_description = models.CharField(
        max_length=100,
        choices=SUB_GROUP_DESCRIPTION_CHOICES,
    )
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="companies_created",
    )

    def __str__(self):
        return self.company_name


class Address(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    region = models.CharField(max_length=100, choices=REGION_CHOICES)
    zone = models.CharField(max_length=100, choices=ZONE_CHOICES)
    woreda = models.CharField(max_length=100, choices=WOREDA_CHOICES)
    house_number = models.CharField(max_length=50, blank=True)
    business_phone_number = models.CharField(max_length=20)
    capital = models.DecimalField(max_digits=15, decimal_places=2)
    site_id = models.CharField(max_length=50, choices=SITE_ID_CHOICES)

    def __str__(self):
        return self.region


class Manager(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="managers",
    )
    manager_full_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    manager_phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.manager_full_name} {self.last_name}"
