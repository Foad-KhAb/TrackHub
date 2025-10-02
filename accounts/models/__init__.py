from rest_framework import serializers
from accounts import Member

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = [
            "id", "email", "first_name", "last_name", "avatar",
            "phone", "title", "bio", "role", "organization",
            "timezone", "language", "preferences", "notification_settings",
            "is_active", "date_joined", "last_seen",
        ]
        read_only_fields = ["id", "is_active", "date_joined", "last_seen"]
