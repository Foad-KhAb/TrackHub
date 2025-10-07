from datetime import timedelta
from django.db.models import Count, Q, Avg, F
from django.utils.dateparse import parse_date
from rest_framework.views import APIView
from rest_framework.response import Response
from tasks.models import Task
from projects.models import Project, Sprint
from projects.permissions import IsProjectMember
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

class BurndownReport(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sprint_id = request.query_params.get("sprint")
        sprint = get_object_or_404(Sprint, pk=sprint_id)
        IsProjectMember().has_object_permission(request, self, sprint.project)

        start, end = sprint.start_date, sprint.end_date
        days = (end - start).days + 1
        series = []
        for i in range(days):
            day = start + timedelta(days=i)
            remaining = Task.objects.filter(sprint=sprint).exclude(status="Done").filter(created_at__date__lte=day).count()
            series.append({"date": str(day), "remaining": remaining})
        return Response({"sprint": sprint.id, "series": series})

class CycleTimeReport(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project_id = request.query_params.get("project")
        project = get_object_or_404(Project, pk=project_id)
        IsProjectMember().has_object_permission(request, self, project)
        # naive cycle time: tasks Done (updated_at - created_at)
        qs = Task.objects.filter(project=project, status="Done").values("id","title","created_at","updated_at")
        data = []
        for t in qs:
            minutes = int((t["updated_at"] - t["created_at"]).total_seconds() // 60)
            data.append({"task": t["id"], "title": t["title"], "cycle_minutes": minutes})
        avg = int(sum(d["cycle_minutes"] for d in data) / len(data)) if data else 0
        return Response({"project": project.id, "average_cycle_minutes": avg, "items": data})

class WorkloadReport(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_id = request.query_params.get("user")
        # tasks per status for user
        agg = (
            Task.objects.filter(assignees__id=user_id)
            .values("status")
            .annotate(count=Count("id"))
        )
        return Response({"user": int(user_id), "by_status": list(agg)})
