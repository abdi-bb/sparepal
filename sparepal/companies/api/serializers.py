from rest_framework import serializers

from sparepal.companies.models import Address
from sparepal.companies.models import Company
from sparepal.companies.models import Manager


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "id",
            "company_name",
            "date_registered",
            "tin_number",
            "renewed_license_date",
            "license_number",
            "legal_status",
            "code",
            "business_description",
            "sub_group_code",
            "sub_group_description",
        ]


class AddressSerializer(serializers.ModelSerializer):
    company = serializers.CharField(read_only=True)

    class Meta:
        model = Address
        fields = "__all__"


class ManagerSerializer(serializers.ModelSerializer):
    company = serializers.CharField(read_only=True)

    class Meta:
        model = Manager
        fields = "__all__"
