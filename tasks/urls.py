from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, ProjectTaskViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    # GET/POST /api/projects/{id}/tasks/
    re_path(r"^projects/(?P<project_id>\d+)/tasks/?$", ProjectTaskViewSet.as_view({"get":"list","post":"create"})),
]

urlpatterns += router.urls
