from rest_framework.permissions import BasePermission
from projects.models import ProjectMembership
from .models import Task

class IsTaskProjectMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        project = obj.project if isinstance(obj, Task) else obj.task.project
        return ProjectMembership.objects.filter(project=project, user=request.user).exists()
