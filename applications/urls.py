from django.urls import path
from .views import (
    JobApplicationListCreateView,
    JobApplicationDetailView,
    KanbanJobApplicationView,
)

urlpatterns = [
    path("", JobApplicationListCreateView.as_view(), name="jobapplication-list-create"),
    path("kanban/", KanbanJobApplicationView.as_view(), name="jobapplication-kanban"),
    path("<int:pk>/", JobApplicationDetailView.as_view(), name="jobapplication-detail"),
]