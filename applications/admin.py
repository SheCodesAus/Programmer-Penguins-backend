from django.contrib import admin
from .models import ApplicationEvent, ApplicationTask, JobApplication

admin.site.register(JobApplication)
admin.site.register(ApplicationTask)
admin.site.register(ApplicationEvent)
