"""
Module for user-related API views.
"""

# Create your views here.
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from decouple import config
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.views import LoginView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext as _
from django.views.generic import RedirectView
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sparepal.users.models import Profile

from .permissions import IsUserProfileOwner
from .serializers import CustomSocialLoginSerializer
from .serializers import CustomUserDetailsSerializer
from .serializers import CustomUserLoginSerializer
from .serializers import CustomUserRegisterSerializer
from .serializers import ProfileDetailsSerializer

User = get_user_model()


class UserRegisterationAPIView(RegisterView):
    """
    Register new users using email and password.
    """

    serializer_class = CustomUserRegisterSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new user.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        response_data = ""

        email = serializer.validated_data.get("email", None)

        if email:
            response_data = {"detail": _("Verification email sent.")}

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


class UserLoginAPIView(LoginView):
    """
    Authenticate existing users using email and password.
    """

    serializer_class = CustomUserLoginSerializer


class ProfileDetailsAPIView(RetrieveUpdateAPIView):
    """
    Get, Update user profile
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileDetailsSerializer
    permission_classes = (IsUserProfileOwner,)

    def get_object(self):
        return self.request.user.profile


class UserDetailsAPIView(RetrieveAPIView):
    """
    Get user details
    """

    queryset = User.objects.all()
    serializer_class = CustomUserDetailsSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class GoogleLogin(SocialLoginView):
    """
    Social authentication with Google
    """

    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = config(
        "CALLBACK_URL",
        default="http://localhost:5000/api/auth/google/",
    )
    serializer_class = CustomSocialLoginSerializer


class UserRedirectView(LoginRequiredMixin, RedirectView):
    """
    (5) This seems to be an error of the library: the dj-rest-auth, at some point,
    checks a redirect URL with the name redirect.
    This is a user redirect URL different from GOOGLE_REDIRECT_URL
    that the flow doesn't need. So, in this case, define a Redirect view:

    This view is needed by the dj-rest-auth-library in order to work the google login.
    It's a bug.
    """

    permanent = False

    def get_redirect_url(self):
        return "redirect-url"


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        """
        Changing the confirmation URL to fit the domain that we are working on
        """

        domain_url = config("DOMAIN_URL", default="http://localhost:3000")
        return f"{domain_url}/auth/verify-account/{emailconfirmation.key}"
