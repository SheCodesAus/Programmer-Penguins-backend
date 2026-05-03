from django.urls import path
from .views import (
    JobApplicationListCreateView,
    JobApplicationDetailView,
    KanbanJobApplicationView,
    AdminJobApplicationListView,
    AdminJobApplicationDetailView,
    AdminRestoreJobApplicationView,
    ApplicationContactListCreateView, 
    ApplicationContactDetailView,
    RestoreApplicationContactView,
    AdminApplicationContactListView,
    AdminAllApplicationContactListView,
    AdminApplicationContactDetailView,
    AdminRestoreApplicationContactView,
    ExtractJobFromUrlView,
)

urlpatterns = [
    path("", JobApplicationListCreateView.as_view(), name="jobapplication-list-create"),
    path("kanban/", KanbanJobApplicationView.as_view(), name="jobapplication-kanban"),

    path("<int:job_id>/contacts/", ApplicationContactListCreateView.as_view(), name="application-contact-list-create"),
    path("contacts/<int:pk>/", ApplicationContactDetailView.as_view(), name="application-contact-detail"),
    path("contacts/<int:pk>/restore/", RestoreApplicationContactView.as_view(), name="application-contact-restore"),
    
    path("admin/contacts/", AdminAllApplicationContactListView.as_view(), name="admin-all-application-contact-list"),
    path("admin/<int:job_id>/contacts/", AdminApplicationContactListView.as_view(), name="admin-application-contact-list"),
    path("admin/contacts/<int:pk>/", AdminApplicationContactDetailView.as_view(), name="admin-application-contact-detail"),
    path("admin/contacts/<int:pk>/restore/", AdminRestoreApplicationContactView.as_view(), name="admin-application-contact-restore"),
    
    path("admin/", AdminJobApplicationListView.as_view(), name="admin-jobapplication-list"),
    path("admin/<int:pk>/", AdminJobApplicationDetailView.as_view(), name="admin-jobapplication-detail"),
    path("admin/<int:pk>/restore/", AdminRestoreJobApplicationView.as_view(), name="admin-jobapplication-restore"),

    path("<int:pk>/", JobApplicationDetailView.as_view(), name="jobapplication-detail"),
    path("extract/", ExtractJobFromUrlView.as_view(), name="extract-job-from-url"),
]