from rest_framework import serializers
from .models import Organization, OrgMembership
from accounts.serializers import MemberSerializer

class OrganizationSerializer(serializers.ModelSerializer):
    members_count = serializers.IntegerField(source="memberships.count", read_only=True)

    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "owner", "members_count", "created_at"]
        read_only_fields = ["id", "slug", "owner", "members_count", "created_at"]

    def create(self, validated):
        user = self.context["request"].user
        org = Organization.objects.create(owner=user, **validated)
        OrgMembership.objects.create(org=org, user=user, role="owner")
        user.organization = org
        user.save(update_fields=["organization"])
        return org

class OrgMembershipSerializer(serializers.ModelSerializer):
    user = MemberSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=MemberSerializer.Meta.model.objects.all(), source="user", write_only=True
    )

    class Meta:
        model = OrgMembership
        fields = ["id", "org", "user", "user_id", "role", "joined_at"]
        read_only_fields = ["id", "joined_at", "org", "user"]
