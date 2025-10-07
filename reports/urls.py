from django.urls import path
from .views import BurndownReport, CycleTimeReport, WorkloadReport

urlpatterns = [
    path("reports/burndown", BurndownReport.as_view()),
    path("reports/cycle-time", CycleTimeReport.as_view()),
    path("reports/workload", WorkloadReport.as_view()),
]
