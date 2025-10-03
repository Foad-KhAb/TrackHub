from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import ProjectMembership

class IsProjectMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return ProjectMembership.objects.filter(project=obj, user=request.user).exists()

class IsProjectAdminOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return ProjectMembership.objects.filter(project=obj, user=request.user).exists()
        return ProjectMembership.objects.filter(project=obj, user=request.user, role__in=["admin"]).exists()
