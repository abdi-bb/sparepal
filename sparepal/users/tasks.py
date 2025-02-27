from celery import shared_task

from .models import CustomUser


@shared_task()
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    return CustomUser.objects.count()
