from django.urls import path

from .views import (
    ChatGPTResourceMetadataView,
    ResourceDetailView,
    ResourceListCreateView,
    ResourceMetadataView,
)


urlpatterns = [
    path("", ResourceListCreateView.as_view(), name="resource-list-create"),
    path("metadata/", ResourceMetadataView.as_view(), name="resource-metadata"),
    path("chatgpt-metadata/", ChatGPTResourceMetadataView.as_view(), name="chatgpt-resource-metadata"),
    path("<int:pk>/", ResourceDetailView.as_view(), name="resource-detail"),
]
