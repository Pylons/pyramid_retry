import pyramid.testing
import pytest

@pytest.fixture
def config():
    config = pyramid.testing.setUp(
        settings={'retry.attempts': 3},
        autocommit=False,
    )
    config.include('pyramid_retry')
    yield config
    pyramid.testing.tearDown()
