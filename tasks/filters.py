import django_filters as df
from .models import Task, Label

class TaskFilter(df.FilterSet):
    status = df.CharFilter(field_name="status")
    label = df.CharFilter(method="filter_label")
    search = df.CharFilter(method="filter_search")

    class Meta:
        model = Task
        fields = ["status"]

    def filter_label(self, qs, name, value):
        return qs.filter(labels__name__iexact=value)

    def filter_search(self, qs, name, value):
        return qs.filter(title__icontains=value) | qs.filter(description__icontains=value)
