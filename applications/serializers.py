from rest_framework import serializers

from .models import JobApplication, ApplicationContact, ApplicationNote


class JobApplicationSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    source_platform_display = serializers.CharField(
        source="get_source_platform_display",
        read_only=True,
    )
    source_platform = serializers.ChoiceField(
        choices=JobApplication.SourcePlatform.choices,
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = JobApplication
        fields = [
            "id",
            "user",
            "job_title",
            "company_name",
            "source_platform",
            "source_platform_display",
            "source_details",
            "job_url",
            "date_posted",
            "date_applied",
            "salary_min",
            "salary_max",
            "currency",
            "location",
            "status",
            "status_display",
            "interest_level",
            "is_active",
            "is_archived",
            "archived_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
            "source_platform_display",
            "status_display",
            "is_archived",
            "archived_at",
        ]


class JobApplicationCreateUpdateSerializer(serializers.ModelSerializer):
    source_platform = serializers.ChoiceField(
        choices=JobApplication.SourcePlatform.choices,
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = JobApplication
        fields = [
            "id",
            "job_title",
            "company_name",
            "source_platform",
            "source_details",
            "job_url",
            "date_posted",
            "date_applied",
            "salary_min",
            "salary_max",
            "currency",
            "location",
            "status",
            "interest_level",
            "is_active",
            "is_archived",
            "archived_at",
        ]
        read_only_fields = [
            "id",
            "archived_at",
        ]

    def validate(self, attrs):
        salary_min = attrs.get("salary_min")
        salary_max = attrs.get("salary_max")
        source_platform = attrs.get("source_platform", "")

        if salary_min is not None and salary_max is not None and salary_min > salary_max:
            raise serializers.ValidationError(
                {"salary_max": "salary_max must be greater than or equal to salary_min."}
            )

        if source_platform != JobApplication.SourcePlatform.OTHER:
            attrs["source_details"] = ""

        interest_level = attrs.get("interest_level")

        if interest_level is not None and (interest_level < 0 or interest_level > 3):
            raise serializers.ValidationError(
                {"interest_level": "Interest level must be between 0 and 3."}
            )

        return attrs
    
class ApplicationContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationContact
        fields = [
            "id",
            "job_application",
            "first_name",
            "last_name",
            "email",
            "phone",
            "note",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "job_application",
            "created_at",
            "updated_at",
        ]
class ApplicationNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationNote
        fields = [
            "id",
            "job_application",
            "title",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "job_application",
            "created_at",
            "updated_at",
        ]