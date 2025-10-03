from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import OrgMembership

class IsOrgMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return OrgMembership.objects.filter(org=obj, user=request.user).exists()

class IsOrgAdminOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return OrgMembership.objects.filter(org=obj, user=request.user).exists()
        return OrgMembership.objects.filter(org=obj, user=request.user, role__in=["owner","admin"]).exists()
