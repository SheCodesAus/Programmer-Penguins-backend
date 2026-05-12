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
    ApplicationNoteListCreateView,
    ApplicationNoteDetailView,
    ApplicationTaskListCreateView,
    ApplicationTaskDetailView,
    CompleteApplicationTaskView,
    ReopenApplicationTaskView,
    ApplicationEventListCreateView,
    ApplicationEventDetailView,
    ArchivedApplicationsView,
    DeletedApplicationsView,
    ArchiveApplicationView,
    RestoreApplicationView,
)

urlpatterns = [
    path("", JobApplicationListCreateView.as_view(), name="jobapplication-list-create"),
    path("kanban/", KanbanJobApplicationView.as_view(), name="jobapplication-kanban"),
    path("archived/", ArchivedApplicationsView.as_view(), name="archived-applications"),
    path("deleted/", DeletedApplicationsView.as_view(), name="deleted-applications"),
    path("<int:pk>/archive/", ArchiveApplicationView.as_view(),name="archive-application"),
    path("<int:pk>/restore/", RestoreApplicationView.as_view(), name="restore-application"),


    path("<int:job_id>/contacts/", ApplicationContactListCreateView.as_view(), name="application-contact-list-create"),
    path("contacts/<int:pk>/", ApplicationContactDetailView.as_view(), name="application-contact-detail"),
    path("contacts/<int:pk>/restore/", RestoreApplicationContactView.as_view(), name="application-contact-restore"),
    
    path("admin/contacts/", AdminAllApplicationContactListView.as_view(), name="admin-all-application-contact-list"),
    path("admin/<int:job_id>/contacts/", AdminApplicationContactListView.as_view(), name="admin-application-contact-list"),
    path("admin/contacts/<int:pk>/", AdminApplicationContactDetailView.as_view(), name="admin-application-contact-detail"),
    path("admin/contacts/<int:pk>/restore/", AdminRestoreApplicationContactView.as_view(), name="admin-application-contact-restore"),

    path("<int:job_id>/notes/", ApplicationNoteListCreateView.as_view(), name="application-notes-list"),
    path("notes/<int:pk>/", ApplicationNoteDetailView.as_view(), name="application-notes-detail"),

    path("tasks/", ApplicationTaskListCreateView.as_view(), name="application-task-list-create"),
    path("tasks/<int:pk>/", ApplicationTaskDetailView.as_view(), name="application-task-detail"),
    path("tasks/<int:pk>/complete/", CompleteApplicationTaskView.as_view(), name="application-task-complete"),
    path("tasks/<int:pk>/reopen/", ReopenApplicationTaskView.as_view(), name="application-task-reopen"),

    path("events/", ApplicationEventListCreateView.as_view(), name="application-event-list-create"),
    path("events/<int:pk>/", ApplicationEventDetailView.as_view(), name="application-event-detail"),
    
    path("admin/", AdminJobApplicationListView.as_view(), name="admin-jobapplication-list"),
    path("admin/<int:pk>/", AdminJobApplicationDetailView.as_view(), name="admin-jobapplication-detail"),
    path("admin/<int:pk>/restore/", AdminRestoreJobApplicationView.as_view(), name="admin-jobapplication-restore"),

    path("<int:pk>/", JobApplicationDetailView.as_view(), name="jobapplication-detail"),
    path("extract/", ExtractJobFromUrlView.as_view(), name="extract-job-from-url"),
]
