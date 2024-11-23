from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

from sparepal.companies.api.views import AddressViewSet
from sparepal.companies.api.views import CompanyViewSet
from sparepal.companies.api.views import GetChoicesAPIView
from sparepal.companies.api.views import ManagerViewSet

# Use DefaultRouter in debug mode for the browsable API; otherwise, use SimpleRouter
router = DefaultRouter() if settings.DEBUG else SimpleRouter()

# Register users-related viewsets


# Register company-related viewsets
# Register companies root-level router
router.register(r"", CompanyViewSet, basename="companies")

# Create nested routers for `Address` and `Manager`
companies_router = routers.NestedDefaultRouter(router, "", lookup="company")

companies_router.register(r"addresses", AddressViewSet, basename="addresses")
companies_router.register(r"managers", ManagerViewSet, basename="managers")

app_name = "companies"
# Base urlpatterns
urlpatterns = router.urls + companies_router.urls


# Non-viewset URLs for company
urlpatterns += [
    path("choices/", GetChoicesAPIView.as_view(), name="get_choices"),
]
