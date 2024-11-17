from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile

User = get_user_model()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


# Signal to manage Supplier group based on is_supplier field
@receiver(post_save, sender=User)
def assign_supplier_group(sender, instance, created, **kwargs):
    supplier_group, _ = Group.objects.get_or_create(name="Supplier")

    # Add to group if is_supplier is True
    if instance.is_supplier:
        if not instance.groups.filter(name="Supplier").exists():
            instance.groups.add(supplier_group)
    # Remove from group if is_supplier is False
    elif instance.groups.filter(name="Supplier").exists():
        instance.groups.remove(supplier_group)
