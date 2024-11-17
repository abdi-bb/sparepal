from django.shortcuts import get_object_or_404

# Correct order of imports
from drf_spectacular.utils import extend_schema
from rest_framework import status

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sparepal.companies.models import BUSINESS_DESCRIPTION_CHOICES
from sparepal.companies.models import LEGAL_STATUS_CHOICES
from sparepal.companies.models import REGION_CHOICES
from sparepal.companies.models import SITE_ID_CHOICES
from sparepal.companies.models import SUB_GROUP_DESCRIPTION_CHOICES
from sparepal.companies.models import WOREDA_CHOICES
from sparepal.companies.models import ZONE_CHOICES
from sparepal.companies.models import Company
from sparepal.companies.models import CompanyDetailAddress
from sparepal.companies.models import CompanyManagerDetail

from .permissions import IsCompanyOwner
from .serializers import CompanyDetailAddressSerializer
from .serializers import CompanyManagerDetailSerializer
from .serializers import CompanySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()  # Default queryset
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsCompanyOwner]

    def get_queryset(self):
        queryset = super().get_queryset()  # Start with the default queryset
        # Filter companies created by the logged-in user
        return queryset.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        # Ensure that the company is created by the current user
        serializer.save(created_by=self.request.user)


class CompanyDetailAddressViewSet(viewsets.ModelViewSet):
    queryset = CompanyDetailAddress.objects.all()
    serializer_class = CompanyDetailAddressSerializer
    permission_classes = [IsAuthenticated, IsCompanyOwner]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter addresses for companies owned by the user
        return queryset.filter(company__created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()  # Make mutable copy of request data
        company_id = data.pop("company_id", None)

        if company_id is None:
            return Response(
                {"error": "company_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            company_id = int(company_id)
        except ValueError:
            return Response(
                {"error": "company_id must be a valid integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        company = get_object_or_404(Company, id=company_id, created_by=request.user)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(company=company)  # Link the address to the company
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CompanyManagerDetailViewSet(viewsets.ModelViewSet):
    queryset = CompanyManagerDetail.objects.all()
    serializer_class = CompanyManagerDetailSerializer
    permission_classes = [IsAuthenticated, IsCompanyOwner]

    def get_queryset(self):
        querset = super().get_queryset()
        # Filter managers for companies owned by the user
        return querset.filter(company__created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()  # Make mutable copy of request data
        company_id = data.pop("company_id", None)

        if company_id is None:
            return Response(
                {"error": "company_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            company_id = int(company_id)
        except ValueError:
            return Response(
                {"error": "company_id must be a valid integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        company = get_object_or_404(Company, id=company_id, created_by=request.user)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(company=company)  # Link the manager to the company
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Django API Endpoint to Serve Choices
@extend_schema(
    responses={
        200: {
            "type": "object",
            "properties": {
                "legal_status": {"type": "array", "items": {"type": "string"}},
                "business_description": {"type": "array", "items": {"type": "string"}},
                "sub_group_description": {"type": "array", "items": {"type": "string"}},
                "region": {"type": "array", "items": {"type": "string"}},
                "zone": {"type": "array", "items": {"type": "string"}},
                "woreda": {"type": "array", "items": {"type": "string"}},
                "site_id": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
)
class GetChoicesAPIView(APIView):
    def get(self, request):
        choices = {
            "legal_status": LEGAL_STATUS_CHOICES,
            "business_description": BUSINESS_DESCRIPTION_CHOICES,
            "sub_group_description": SUB_GROUP_DESCRIPTION_CHOICES,
            "region": REGION_CHOICES,
            "zone": ZONE_CHOICES,
            "woreda": WOREDA_CHOICES,
            "site_id": SITE_ID_CHOICES,
        }

        return Response(choices, status=status.HTTP_200_OK)
