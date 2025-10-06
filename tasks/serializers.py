from rest_framework import serializers
from .models import Task, Label, Attachment, Comment, TimeEntry

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ["id","project","name","color"]
        read_only_fields = ["id","project"]

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ["id","file","uploaded_by","uploaded_at"]
        read_only_fields = ["id","uploaded_by","uploaded_at"]

class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.full_name", read_only=True)
    class Meta:
        model = Comment
        fields = ["id","author","author_name","body","created_at"]
        read_only_fields = ["id","author","author_name","created_at"]

class TimeEntrySerializer(serializers.ModelSerializer):
    duration_minutes = serializers.IntegerField(read_only=True)
    class Meta:
        model = TimeEntry
        fields = ["id","user","started_at","ended_at","note","duration_minutes"]
        read_only_fields = ["id","user","duration_minutes"]

class TaskSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True, read_only=True)
    label_ids = serializers.PrimaryKeyRelatedField(queryset=Label.objects.all(), many=True, write_only=True, required=False)
    assignee_ids = serializers.PrimaryKeyRelatedField(many=True, write_only=True, required=False, source="assignees",
                                                     queryset=type(TimeEntry._meta.get_field('user')).remote_field.model.objects.all())
    class Meta:
        model = Task
        fields = [
            "id","project","sprint","title","description","status","order","due_date",
            "labels","label_ids","assignee_ids","created_at","updated_at"
        ]
        read_only_fields = ["id","created_at","updated_at"]

    def create(self, validated):
        label_ids = validated.pop("label_ids", [])
        assignees = validated.pop("assignees", [])
        task = super().create(validated)
        if label_ids: task.labels.set(label_ids)
        if assignees: task.assignees.set(assignees)
        return task

    def update(self, instance, validated):
        label_ids = validated.pop("label_ids", None)
        assignees = validated.pop("assignees", None)
        task = super().update(instance, validated)
        if label_ids is not None: task.labels.set(label_ids)
        if assignees is not None: task.assignees.set(assignees)
        return task
