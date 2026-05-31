from django.urls import path
from .views import FeedbackMessageCreateView

urlpatterns = [
    path("", FeedbackMessageCreateView.as_view(), name="feedback-create"),
]