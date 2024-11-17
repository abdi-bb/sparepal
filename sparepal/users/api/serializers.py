from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from rest_framework import serializers

from sparepal.users.models import Profile

from .exceptions import AccountDisabledException
from .exceptions import InvalidCredentialsException

User = get_user_model()


class ProfileDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer class to convert Profile model instances to JSON.
    """

    class Meta:
        model = Profile
        fields = (
            "avatar",
            "bio",
            "created_at",
            "updated_at",
        )


class CustomUserDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer class to convert User model instances to JSON.
    """

    profile = ProfileDetailsSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_supplier",
            "profile",
        )


class CustomUserRegisterSerializer(RegisterSerializer):
    """
    Serializer class to register a new user using email.
    """

    username = None
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    email = serializers.EmailField(required=True)
    is_supplier = serializers.BooleanField(default=False)  # Checkbox field

    def validate(self, validated_data):
        """
        Validate the user registration data.
        """

        email = validated_data.get("email", None)

        error_email_required = _("Enter an email address.")

        if not email:
            raise serializers.ValidationError(error_email_required)

        error_password_donot_match = _("The two password fields didn't match.")

        if validated_data["password1"] != validated_data["password2"]:
            raise serializers.ValidationError(error_password_donot_match)

        return validated_data

    # Override the get_cleaned_data method to include first_name and last_name
    def get_cleaned_data(self):
        """
        Get the cleaned data.
        """

        cleaned_data = super().get_cleaned_data()
        cleaned_data["first_name"] = self.validated_data.get("first_name", "")
        cleaned_data["last_name"] = self.validated_data.get("last_name", "")

        return cleaned_data

    # Override the save method to include first_name, last_name and is_supplier
    def save(self, request):
        """
        Save the user.
        """

        user = super().save(request)
        user.first_name = self.validated_data.get("first_name", "")
        user.last_name = self.validated_data.get("last_name", "")
        user.is_supplier = self.validated_data.get("is_supplier", False)
        user.save()

        return user


class CustomUserLoginSerializer(serializers.Serializer):
    """
    Serializer class to login a user using email.
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def _validate_email(self, email, password):
        """
        Validate the email and password.
        """

        user = None

        if email and password:
            user = authenticate(email=email, password=password)
        else:
            raise serializers.ValidationError(
                _('Must include "email" and "password".'),
            )

        return user

    def validate(self, validated_data):
        """
        Validate the user login data.
        """

        email = validated_data.get("email")
        password = validated_data.get("password")

        user = None

        user = self._validate_email(email, password)

        if not user:
            raise InvalidCredentialsException

        if not user.is_active:
            raise AccountDisabledException

        if email:
            email_address = user.emailaddress_set.filter(
                email=user.email,
                verified=True,
            ).first()
            if not email_address:
                raise serializers.ValidationError(_("Email address is not verified."))

        validated_data["user"] = user

        return validated_data
