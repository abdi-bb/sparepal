import pytest

from sparepal.users.models import CustomUser
from sparepal.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> CustomUser:
    return UserFactory()
