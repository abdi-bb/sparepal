# Create your models here.
# Create your models here.
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from PIL import Image

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    A CustomUser model that extends Django's AbstractBaseUser model. This model is used
    to create a custom user model that uses email as the unique identifier instead of
    the default username and eliminates the need for a username field.

    Email and password are required. Other fields are optional.
    """

    username_validator = ASCIIUsernameValidator()

    email = models.EmailField(
        _("email address"),
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
        ),
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts.",
        ),
    )
    is_supplier = models.BooleanField(
        _("supplier status"),
        default=False,
        help_text=_(
            "Designates whether the user is a supplier and can create a company or is \
                simply a regular user.",
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    # Make email case-insensitive
    def get_by_natural_key(self, email):
        case_insensitive_email_field = f"{self.EMAIL_FIELD}__iexact"
        return self.get(**{case_insensitive_email_field: email})

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return self.email

    @property
    def name(self):
        """
        Dynamic 'name' property to provide compatibility with code expecting
        a 'name' attribute(Eg. SocialAccountAdapter).
        It uses the get_full_name() method.
        """
        return self.get_full_name()


class Profile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        related_name="profile",
        on_delete=models.CASCADE,
    )
    avatar = models.ImageField(default="default.png", upload_to="avatars/", blank=True)
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.user.email

    # resize image
    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.avatar.path)

        max_image_dimension = 100
        if img.height > max_image_dimension or img.width > max_image_dimension:
            new_img = (100, 100)
            img.thumbnail(new_img)
            img.save(self.avatar.path)

    def activeness(self):
        if self.user.is_active:
            return "Active"
        return "Inactive"
