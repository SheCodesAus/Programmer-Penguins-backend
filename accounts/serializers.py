from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Profile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "is_active",
            "is_staff",
            "date_joined",
        ]


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "desired_role",
            "industry",
            "years_of_experience",
            "location",
            "phone",
            "linkedin_url",
            "gender",
            "gender_self_described",
            "career_goal",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        gender = attrs.get("gender")
        gender_self_described = attrs.get("gender_self_described")

        if gender == "self_describe" and not gender_self_described:
            raise serializers.ValidationError({
                "gender_self_described": "This field is required when gender is 'self_describe'."
            })

        if gender != "self_describe":
            attrs["gender_self_described"] = ""

        return attrs

class ProfileWithUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "desired_role",
            "industry",
            "years_of_experience",
            "location",
            "phone",
            "linkedin_url",
            "gender",
            "gender_self_described",
            "career_goal",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]