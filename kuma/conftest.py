import pytest
import requests_mock
from django.contrib.auth.models import Group
from django.core.cache import caches
from django.urls import set_urlconf
from django.utils import timezone
from django.utils.translation import activate

from kuma.users.models import UserProfile


@pytest.fixture(autouse=True)
def clear_cache():
    """
    Before every pytest test function starts, it clears the cache.
    """
    caches["default"].clear()


@pytest.fixture(autouse=True)
def set_default_language():
    activate("en-US")


@pytest.fixture(autouse=True)
def reset_urlconf():
    """
    Reset the default urlconf used by "reverse" to the one provided
    by settings.ROOT_URLCONF.

    Django resets the default urlconf back to settings.ROOT_URLCONF at
    the beginning of each request, but if the incoming request has a
    "urlconf" attribute, the default urlconf is changed to its value for
    the remainder of the request, so that all subsequent "reverse" calls
    use that value (unless they explicitly specify a different one). The
    problem occurs when a test is run that uses the "request.urlconf"
    mechanism, setting the default urlconf to something other than
    settings.ROOT_URLCONF, and then subsequent tests make "reverse" calls
    that fail because they're expecting a default urlconf of
    settings.ROOT_URLCONF (i.e., they're not explicitly providing a
    urlconf value to the "reverse" call).
    """
    set_urlconf(None)
    yield
    set_urlconf(None)


@pytest.fixture
def beta_testers_group(db):
    return Group.objects.create(name="Beta Testers")


@pytest.fixture
def wiki_user(db, django_user_model):
    """A test user."""
    return django_user_model.objects.create(
        username="wiki_user",
        email="wiki_user@example.com",
        date_joined=timezone.now(),
    )


@pytest.fixture
def user_client(client, wiki_user):
    """A test client with wiki_user logged in."""
    wiki_user.set_password("password")
    wiki_user.save()
    client.login(username=wiki_user.username, password="password")
    return client


@pytest.fixture
def subscriber_client(client, wiki_user):
    """A test client with wiki_user logged in and a paying subscriber."""
    UserProfile.objects.create(user=wiki_user)
    wiki_user.set_password("password")
    wiki_user.save()
    client.login(username=wiki_user.username, password="password")
    return client


@pytest.fixture
def stripe_user(wiki_user):
    wiki_user.stripe_customer_id = "fakeCustomerID123"
    wiki_user.save()
    return wiki_user


@pytest.fixture
def stripe_user_client(client, stripe_user):
    """A test client with wiki_user logged in and with a stripe_customer_id."""
    stripe_user.set_password("password")
    stripe_user.save()
    client.login(username=stripe_user.username, password="password")
    return client


@pytest.fixture
def mock_requests():
    with requests_mock.Mocker() as mocker:
        yield mocker
