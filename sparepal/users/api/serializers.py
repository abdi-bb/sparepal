from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.http import HttpResponseBadRequest
from django.utils.translation import gettext_lazy as _
from requests.exceptions import HTTPError
from rest_framework import serializers

try:
    from allauth.account import app_settings as allauth_account_settings
    from allauth.socialaccount.helpers import complete_social_login
except ImportError as err:
    ALLAUTH_MISSING_ERROR = "allauth needs to be added to INSTALLED_APPS."
    raise ImportError(ALLAUTH_MISSING_ERROR) from err

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


# Fix compatiblity issue between django_allath>0.61.1 and dj-rest-auth
# Make dj-rest-auth to use get_scope_from_request inplace of get_scope


# ruff: noqa: C901, PLR0912, PLR0915
class CustomSocialLoginSerializer(SocialLoginSerializer):
    def validate(self, attrs):
        view = self.context.get("view")
        request = self._get_request()

        if not view:
            raise serializers.ValidationError(
                _("View is not defined, pass it as a context variable"),
            )

        adapter_class = getattr(view, "adapter_class", None)
        if not adapter_class:
            raise serializers.ValidationError(_("Define adapter_class in view"))

        adapter = adapter_class(request)
        app = adapter.get_provider().app

        # More info on code vs access_token
        # http://stackoverflow.com/questions/8666316/facebook-oauth-2-0-code-and-token

        access_token = attrs.get("access_token")
        code = attrs.get("code")
        # Case 1: We received the access_token
        if access_token:
            tokens_to_parse = {"access_token": access_token}
            token = access_token
            # For sign in with apple
            id_token = attrs.get("id_token")
            if id_token:
                tokens_to_parse["id_token"] = id_token

        # Case 2: We received the authorization code
        elif code:
            self.set_callback_url(view=view, adapter_class=adapter_class)
            self.client_class = getattr(view, "client_class", None)

            if not self.client_class:
                raise serializers.ValidationError(
                    _("Define client_class in view"),
                )

            provider = adapter.get_provider()
            scope = provider.get_scope_from_request(request)
            client = self.client_class(
                request,
                app.client_id,
                app.secret,
                adapter.access_token_method,
                adapter.access_token_url,
                self.callback_url,
                scope,
                headers=adapter.headers,
                basic_auth=adapter.basic_auth,
            )
            try:
                token = client.get_access_token(code)
            except OAuth2Error as ex:
                raise serializers.ValidationError(
                    _("Failed to exchange code for access token"),
                ) from ex
            access_token = token["access_token"]
            tokens_to_parse = {"access_token": access_token}

            # If available we add additional data to the dictionary
            for key in ["refresh_token", "id_token", adapter.expires_in_key]:
                if key in token:
                    tokens_to_parse[key] = token[key]
        else:
            raise serializers.ValidationError(
                _("Incorrect input. access_token or code is required."),
            )

        social_token = adapter.parse_token(tokens_to_parse)
        social_token.app = app

        try:
            if adapter.provider_id == "google" and not code:
                login = self.get_social_login(
                    adapter,
                    app,
                    social_token,
                    response={"id_token": id_token},
                )
            else:
                login = self.get_social_login(adapter, app, social_token, token)
            ret = complete_social_login(request, login)
        except HTTPError as err:
            incorrect_value_err = "An error occurred: Incorrect value"
            raise serializers.ValidationError(_(incorrect_value_err)) from err

        if isinstance(ret, HttpResponseBadRequest):
            raise serializers.ValidationError(ret.content)

        if not login.is_existing:
            # We have an account already signed up in a different flow
            # with the same email address: raise an exception.
            # This needs to be handled in the frontend. We can not just
            # link up the accounts due to security constraints
            if allauth_account_settings.UNIQUE_EMAIL:
                # Do we have an account already with this email address?
                account_exists = (
                    get_user_model()
                    .objects.filter(
                        email=login.user.email,
                    )
                    .exists()
                )
                if account_exists:
                    raise serializers.ValidationError(
                        _("User is already registered with this e-mail address."),
                    )

            login.lookup()
            try:
                login.save(request, connect=True)
            except IntegrityError as ex:
                raise serializers.ValidationError(
                    _("User is already registered with this e-mail address."),
                ) from ex
            self.post_signup(login, attrs)

        attrs["user"] = login.account.user

        return attrs
