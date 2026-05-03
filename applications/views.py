import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from rest_framework.views import APIView
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import JobApplication, ApplicationContact
from .serializers import (
    JobApplicationSerializer,
    JobApplicationCreateUpdateSerializer,
    ApplicationContactSerializer,
)

def detect_source_platform(url):
    domain = urlparse(url).netloc.lower()

    if "seek.com" in domain:
        return JobApplication.SourcePlatform.SEEK
    if "linkedin.com" in domain:
        return JobApplication.SourcePlatform.LINKEDIN
    if "indeed.com" in domain:
        return JobApplication.SourcePlatform.INDEED

    return JobApplication.SourcePlatform.OTHER

def extract_json_ld_job_posting(soup):
    scripts = soup.find_all("script", type="application/ld+json")

    for script in scripts:
        try:
            data = json.loads(script.string)

            if isinstance(data, list):
                for item in data:
                    if item.get("@type") == "JobPosting":
                        return item

            if isinstance(data, dict):
                if data.get("@type") == "JobPosting":
                    return data

                graph = data.get("@graph", [])
                for item in graph:
                    if item.get("@type") == "JobPosting":
                        return item

        except Exception:
            continue

    return None

def parse_job_posting_json_ld(data):
    company = data.get("hiringOrganization", {})
    location_data = data.get("jobLocation", {})
    salary_data = data.get("baseSalary", {})

    result = {
        "job_title": data.get("title", "") or "",
        "company_name": company.get("name", "") if isinstance(company, dict) else "",
        "date_posted": data.get("datePosted"),
        "location": "",
        "currency": "AUD",
        "salary_min": None,
        "salary_max": None,
    }

    if isinstance(location_data, list) and location_data:
        location_data = location_data[0]

    if isinstance(location_data, dict):
        address = location_data.get("address", {})
        if isinstance(address, dict):
            locality = address.get("addressLocality", "")
            region = address.get("addressRegion", "")
            country = address.get("addressCountry", "")

            result["location"] = ", ".join(
                part for part in [locality, region, country] if part
            )

    if isinstance(salary_data, dict):
        result["currency"] = salary_data.get("currency", "AUD") or "AUD"

        value = salary_data.get("value", {})
        if isinstance(value, dict):
            min_value = value.get("minValue")
            max_value = value.get("maxValue")
            single_value = value.get("value")

            result["salary_min"] = min_value or single_value
            result["salary_max"] = max_value or single_value

    return result

class JobApplicationListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post"]

    def get_queryset(self):
        queryset = JobApplication.objects.filter(user=self.request.user).order_by("-created_at")

        status_param = self.request.query_params.get("status")
        source_platform = self.request.query_params.get("source_platform")
        is_active = self.request.query_params.get("is_active")

        if status_param:
            queryset = queryset.filter(status=status_param)

        if source_platform:
            queryset = queryset.filter(source_platform=source_platform)

        if is_active is not None:
            if is_active.lower() == "true":
                queryset = queryset.filter(is_active=True)
            elif is_active.lower() == "false":
                queryset = queryset.filter(is_active=False)

        return queryset

    def get_serializer_class(self):
        if self.request.method == "POST":
            return JobApplicationCreateUpdateSerializer
        return JobApplicationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class JobApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch", "delete"]

    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return JobApplicationCreateUpdateSerializer
        return JobApplicationSerializer

    def destroy(self, request, *args, **kwargs):
        application = self.get_object()
        application.is_active = False
        application.save()

        return Response(
            {"detail": "Job application has been deactivated successfully."},
            status=status.HTTP_200_OK,
        )


class KanbanJobApplicationView(generics.ListAPIView):
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get"]

    def get_queryset(self):
        return JobApplication.objects.filter(
            user=self.request.user,
            is_active=True,
        ).order_by("-updated_at")


class ExtractJobFromUrlView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        url = request.data.get("url", "").strip()

        if not url:
            return Response(
                {"error": "URL is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        platform = detect_source_platform(url)

        extracted_data = {
            "job_title": "",
            "company_name": "",
            "source_platform": platform,
            "source_details": "",
            "job_url": url,
            "date_posted": None,
            "salary_min": None,
            "salary_max": None,
            "currency": "AUD",
            "location": "",
            "notes": "",
        }

        try:
            response = requests.get(
                url,
                timeout=10,
                headers={
                    "User-Agent": "Mozilla/5.0"
                },
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            json_ld_data = extract_json_ld_job_posting(soup)

            if json_ld_data:
                extracted_data.update(parse_job_posting_json_ld(json_ld_data))
            else:
                title = soup.find("title")
                if title:
                    extracted_data["job_title"] = title.get_text(strip=True)

        except Exception:
            extracted_data["notes"] = "Could not fully extract details from this link."

        return Response(extracted_data)

class AdminJobApplicationListView(generics.ListAPIView):
    queryset = JobApplication.objects.select_related("user").order_by("-created_at")
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["get"]


class AdminJobApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = JobApplication.objects.select_related("user")
    permission_classes = [IsAdminUser]
    http_method_names = ["get", "patch", "delete"]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return JobApplicationCreateUpdateSerializer
        return JobApplicationSerializer

    def destroy(self, request, *args, **kwargs):
        application = self.get_object()
        application.is_active = False
        application.save()

        return Response(
            {"detail": "Job application has been deactivated successfully."},
            status=status.HTTP_200_OK,
        )


class AdminRestoreJobApplicationView(generics.GenericAPIView):
    queryset = JobApplication.objects.all()
    permission_classes = [IsAdminUser]
    http_method_names = ["patch"]

    def patch(self, request, pk):
        application = self.get_object()
        application.is_active = True
        application.save()

        return Response(
            {"detail": "Job application has been restored successfully."},
            status=status.HTTP_200_OK,
        )
    
class ApplicationContactListCreateView(generics.ListCreateAPIView):
    serializer_class = ApplicationContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        job_id = self.kwargs["job_id"]

        return ApplicationContact.objects.filter(
            job_application__id=job_id,
            job_application__user=self.request.user,
            is_active=True,
        )

    def perform_create(self, serializer):
        job_id = self.kwargs["job_id"]
        job = JobApplication.objects.get(id=job_id, user=self.request.user)
        serializer.save(job_application=job)


class ApplicationContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ApplicationContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch", "delete"]

    def get_queryset(self):
        return ApplicationContact.objects.filter(
            job_application__user=self.request.user
        )

    def destroy(self, request, *args, **kwargs):
        contact = self.get_object()
        contact.is_active = False
        contact.save()

        return Response(
            {"detail": "Application contact has been deleted successfully."},
            status=status.HTTP_200_OK,
        )


class RestoreApplicationContactView(generics.GenericAPIView):
    serializer_class = ApplicationContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["patch"]

    def get_queryset(self):
        return ApplicationContact.objects.filter(
            job_application__user=self.request.user
        )

    def patch(self, request, pk):
        contact = self.get_object()
        contact.is_active = True
        contact.save()

        return Response(
            {"detail": "Application contact has been restored successfully."},
            status=status.HTTP_200_OK,
        )
    
class AdminApplicationContactListView(generics.ListAPIView):
    serializer_class = ApplicationContactSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["get"]

    def get_queryset(self):
        job_id = self.kwargs["job_id"]

        return ApplicationContact.objects.filter(
            job_application__id=job_id
        ).order_by("-created_at")
    
class AdminAllApplicationContactListView(generics.ListAPIView):
    serializer_class = ApplicationContactSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["get"]

    def get_queryset(self):
        return ApplicationContact.objects.all().order_by("-created_at")


class AdminApplicationContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ApplicationContactSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["get", "patch", "delete"]

    def get_queryset(self):
        return ApplicationContact.objects.all()

    def destroy(self, request, *args, **kwargs):
        contact = self.get_object()
        contact.is_active = False
        contact.save()

        return Response(
            {"detail": "Application contact has been deleted successfully."},
            status=status.HTTP_200_OK,
        )


class AdminRestoreApplicationContactView(generics.GenericAPIView):
    serializer_class = ApplicationContactSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["patch"]

    def get_queryset(self):
        return ApplicationContact.objects.all()

    def patch(self, request, pk):
        contact = self.get_object()
        contact.is_active = True
        contact.save()

        return Response(
            {"detail": "Application contact has been restored successfully."},
            status=status.HTTP_200_OK,
        )

class AdminAllApplicationContactListView(generics.ListAPIView):
    serializer_class = ApplicationContactSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = ApplicationContact.objects.all().order_by("-created_at")

        is_active = self.request.query_params.get("is_active")

        if is_active is not None:
            if is_active.lower() == "true":
                queryset = queryset.filter(is_active=True)
            elif is_active.lower() == "false":
                queryset = queryset.filter(is_active=False)

        return queryset
    
class AdminApplicationContactListView(generics.ListAPIView):
    serializer_class = ApplicationContactSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["get"]

    def get_queryset(self):
        job_id = self.kwargs["job_id"]

        queryset = ApplicationContact.objects.filter(
            job_application__id=job_id
        ).order_by("-created_at")

        is_active = self.request.query_params.get("is_active")

        if is_active is not None:
            if is_active.lower() == "true":
                queryset = queryset.filter(is_active=True)
            elif is_active.lower() == "false":
                queryset = queryset.filter(is_active=False)

        return queryset