from rest_framework.permissions import BasePermission

from sparepal.companies.models import Company


class IsCompanyOwner(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.groups.filter(name="Supplier").exists()
            or request.user.is_supplier
        )

    def has_object_permission(self, request, view, obj):
        # Check if the user owns the company
        return isinstance(obj, Company) and obj.created_by == request.user
