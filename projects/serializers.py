from rest_framework import serializers
from .models import Project, ProjectMembership, Sprint, ProjectInvite

class ProjectSerializer(serializers.ModelSerializer):
    members_count = serializers.IntegerField(source="memberships.count", read_only=True)
    class Meta:
        model = Project
        fields = ["id","org","name","key","description","is_private","members_count","created_at"]
        read_only_fields = ["id","members_count","created_at"]

class ProjectInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectInvite
        fields = ["id","email","token","created_at","accepted_at"]
        read_only_fields = ["id","token","created_at","accepted_at"]
