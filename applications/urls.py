from django.urls import path
from .views import (
    JobApplicationListCreateView,
    JobApplicationDetailView,
    KanbanJobApplicationView,
    AdminJobApplicationListView,
    AdminJobApplicationDetailView,
    AdminRestoreJobApplicationView,
)

urlpatterns = [
    path("", JobApplicationListCreateView.as_view(), name="jobapplication-list-create"),
    path("kanban/", KanbanJobApplicationView.as_view(), name="jobapplication-kanban"),
    path("<int:pk>/", JobApplicationDetailView.as_view(), name="jobapplication-detail"),

    path("admin/", AdminJobApplicationListView.as_view(), name="admin-jobapplication-list"),
    path("admin/<int:pk>/", AdminJobApplicationDetailView.as_view(), name="admin-jobapplication-detail"),
    path("admin/<int:pk>/restore/", AdminRestoreJobApplicationView.as_view(), name="admin-jobapplication-restore"),
]