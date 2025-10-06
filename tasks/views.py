from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.shortcuts import get_object_or_404
from .models import Task, Label, Attachment, Comment, TimeEntry
from .serializers import TaskSerializer, LabelSerializer, AttachmentSerializer, CommentSerializer, TimeEntrySerializer
from .filters import TaskFilter
from .permissions import IsTaskProjectMember
from projects.models import Project
from projects.permissions import IsProjectMember

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    filterset_class = TaskFilter
    search_fields = ["title","description"]
    ordering_fields = ["created_at","updated_at","order","due_date"]

    def get_queryset(self):
        user = self.request.user
        qs = Task.objects.filter(project__memberships__user=user).select_related("project","sprint").prefetch_related("labels","assignees")
        project_id = self.request.query_params.get("project")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs.distinct()

    def get_permissions(self):
        if self.action in ["list","create","retrieve"]:
            return []
        return [IsTaskProjectMember()]

    # POST /api/tasks/{id}/move
    @action(detail=True, methods=["post"])
    def move(self, request, pk=None):
        task = self.get_object()
        new_status = request.data.get("status")
        new_order = request.data.get("order", 0)
        if new_status:
            task.status = new_status
        if new_order is not None:
            task.order = int(new_order)
        task.save(update_fields=["status","order"])
        return Response(TaskSerializer(task).data)

    # POST /api/tasks/{id}/assign
    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        task = self.get_object()
        user_ids = request.data.get("user_ids", [])
        task.assignees.set(user_ids)
        return Response({"detail":"assigned"})

    # POST /api/tasks/{id}/labels
    @action(detail=True, methods=["post"])
    def labels(self, request, pk=None):
        task = self.get_object()
        label_ids = request.data.get("label_ids", [])
        task.labels.set(label_ids)
        return Response({"detail":"labels set"})

    # POST /api/tasks/{id}/attachments
    @action(detail=True, methods=["post"], parser_classes=[MultiPartParser])
    def attachments(self, request, pk=None):
        task = self.get_object()
        ser = AttachmentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        att = Attachment.objects.create(task=task, uploaded_by=request.user, **ser.validated_data)
        return Response(AttachmentSerializer(att).data, status=201)

    # GET/POST /api/tasks/{id}/comments/
    @action(detail=True, methods=["get","post"], url_path="comments")
    def comments(self, request, pk=None):
        task = self.get_object()
        if request.method == "GET":
            return Response(CommentSerializer(task.comments.all(), many=True).data)
        ser = CommentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        c = task.comments.create(author=request.user, **ser.validated_data)
        return Response(CommentSerializer(c).data, status=201)

    # GET/POST /api/tasks/{id}/time-entries/
    @action(detail=True, methods=["get","post"], url_path="time-entries")
    def time_entries(self, request, pk=None):
        task = self.get_object()
        if request.method == "GET":
            return Response(TimeEntrySerializer(task.time_entries.all(), many=True).data)
        ser = TimeEntrySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        te = task.time_entries.create(user=request.user, **ser.validated_data)
        return Response(TimeEntrySerializer(te).data, status=201)

class ProjectTaskViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    serializer_class = TaskSerializer
    filterset_class = TaskFilter

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs["project_id"])
        # permissions: member of project
        self.check_object_permissions(self.request, project)
        return project.tasks.all().select_related("project","sprint").prefetch_related("labels","assignees")

    def get_permissions(self):
        return [IsProjectMember()]
