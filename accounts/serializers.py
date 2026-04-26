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


class CombinedProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        required=False,
        allow_blank=False,
    )
    email = serializers.EmailField(
        source="user.email",
        required=False,
    )
    first_name = serializers.CharField(
        source="user.first_name",
        required=False,
        allow_blank=True,
    )
    last_name = serializers.CharField(
        source="user.last_name",
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
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

    def validate(self, attrs):
        gender = attrs.get("gender")
        gender_self_described = attrs.get("gender_self_described")

        if gender == "self_describe" and not gender_self_described:
            raise serializers.ValidationError({
                "gender_self_described": "This field is required when gender is 'self_describe'."
            })

        if gender and gender != "self_describe":
            attrs["gender_self_described"] = ""

        user_data = attrs.get("user", {})
        username = user_data.get("username")
        email = user_data.get("email")

        if username:
            username_exists = User.objects.filter(username=username).exclude(
                pk=self.instance.user.pk
            ).exists()

            if username_exists:
                raise serializers.ValidationError({
                    "username": "This username is already taken."
                })

        if email:
            email_exists = User.objects.filter(email=email).exclude(
                pk=self.instance.user.pk
            ).exists()

            if email_exists:
                raise serializers.ValidationError({
                    "email": "This email is already registered."
                })

        return attrs

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})

        user = instance.user

        for attr, value in user_data.items():
            setattr(user, attr, value)

        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance