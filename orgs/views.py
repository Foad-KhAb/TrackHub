from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Organization, OrgMembership
from .serializers import OrganizationSerializer, OrgMembershipSerializer
from .permissions import IsOrgMember, IsOrgAdminOrReadOnly

class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        user = self.request.user
        return Organization.objects.filter(memberships__user=user).distinct()

    def perform_create(self, serializer):
        serializer.save()  # serializer handles owner + membership

    def get_permissions(self):
        if self.action in ["list", "create"]:
            return []
        return [IsOrgAdminOrReadOnly()]

    @action(detail=True, methods=["get","post"], url_path="members")
    def members(self, request, pk=None):
        org = self.get_object()
        if request.method == "GET":
            qs = OrgMembership.objects.filter(org=org).select_related("user")
            return Response(OrgMembershipSerializer(qs, many=True).data)
        # POST add member by user_id
        serializer = OrgMembershipSerializer(data=request.data, context={"request":request})
        serializer.is_valid(raise_exception=True)
        OrgMembership.objects.create(org=org, user=serializer.validated_data["user"], role=request.data.get("role","member"))
        return Response({"detail": "Member added"}, status=201)
