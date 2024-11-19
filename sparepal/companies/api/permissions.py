from rest_framework.permissions import BasePermission

from sparepal.companies.models import Address
from sparepal.companies.models import Company
from sparepal.companies.models import Manager


class IsCompanyOwner(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.groups.filter(name="Supplier").exists()
            or request.user.is_supplier
        )

    def has_object_permission(self, request, view, obj):
        # Check if the user owns the company
        return (isinstance(obj, Company) and obj.created_by == request.user) or (
            isinstance(obj, (Address, Manager))
            and obj.company.created_by == request.user
        )
