import secrets
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from orgs.models import OrgMembership
from .models import Project, ProjectMembership, ProjectInvite
from .serializers import ProjectSerializer, ProjectInviteSerializer
from .permissions import IsProjectAdminOrReadOnly

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(memberships__user=user).select_related("org").distinct()

    def perform_create(self, serializer):
        project = serializer.save()
        # ensure org membership
        OrgMembership.objects.get_or_create(org=project.org, user=self.request.user, defaults={"role":"admin"})
        ProjectMembership.objects.create(project=project, user=self.request.user, role="admin")

    def get_permissions(self):
        if self.action in ["list", "create"]:
            return []
        return [IsProjectAdminOrReadOnly()]

    @action(detail=True, methods=["post"], url_path="invite")
    def invite(self, request, pk=None):
        project = self.get_object()
        email = request.data.get("email")
        if not email:
            return Response({"detail":"email required"}, status=400)
        inv = ProjectInvite.objects.create(project=project, email=email, token=secrets.token_urlsafe(32))
        # (send email out-of-scope)
        return Response(ProjectInviteSerializer(inv).data, status=201)
