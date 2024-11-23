from django.urls import include
from django.urls import path

urlpatterns = [
    path("", include("sparepal.users.api.urls", namespace="users")),
    path("companies/", include("sparepal.companies.api.urls", namespace="companies")),
    # Your stuff: custom urls includes go here
]
