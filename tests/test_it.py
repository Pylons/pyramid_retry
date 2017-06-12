import pyramid.request
import pyramid.testing
import pytest
import webtest

def test_raising_RetryableException_is_caught(config):
    from pyramid_retry import RetryableException
    calls = []
    def final_view(request):
        calls.append('ok')
        return 'ok'
    def bad_view(request):
        calls.append('fail')
        raise RetryableException
    config.add_view(bad_view, last_retry_attempt=False)
    config.add_view(final_view, last_retry_attempt=True, renderer='string')
    app = config.make_wsgi_app()
    app = webtest.TestApp(app)
    response = app.get('/')
    assert response.body == b'ok'
    assert calls == ['fail', 'fail', 'ok']

def test_raising_IRetryableError_instance_is_caught(config):
    from pyramid_retry import mark_error_retryable
    calls = []
    def final_view(request):
        calls.append('ok')
        return 'ok'
    def bad_view(request):
        calls.append('fail')
        ex = Exception()
        mark_error_retryable(ex)
        raise ex
    config.add_view(bad_view, last_retry_attempt=False)
    config.add_view(final_view, last_retry_attempt=True, renderer='string')
    app = config.make_wsgi_app()
    app = webtest.TestApp(app)
    response = app.get('/')
    assert response.body == b'ok'
    assert calls == ['fail', 'fail', 'ok']

def test_raising_IRetryableError_type_is_caught(config):
    from pyramid_retry import mark_error_retryable
    class MyRetryableError(Exception):
        pass
    mark_error_retryable(MyRetryableError)
    calls = []
    def final_view(request):
        calls.append('ok')
        return 'ok'
    def bad_view(request):
        calls.append('fail')
        raise MyRetryableError
    config.add_view(bad_view, last_retry_attempt=False)
    config.add_view(final_view, last_retry_attempt=True, renderer='string')
    app = config.make_wsgi_app()
    app = webtest.TestApp(app)
    response = app.get('/')
    assert response.body == b'ok'
    assert calls == ['fail', 'fail', 'ok']

def test_raising_nonretryable_is_not_caught(config):
    calls = []
    def bad_view(request):
        calls.append('fail')
        raise Exception
    config.add_view(bad_view)
    app = config.make_wsgi_app()
    app = webtest.TestApp(app)
    with pytest.raises(Exception):
        app.get('/')
    assert calls == ['fail']


def test_handled_error_is_retried(config):
    from pyramid_retry import RetryableException
    calls = []
    def bad_view(request):
        calls.append('fail')
        raise RetryableException
    def retryable_exc_view(request):
        calls.append('caught')
        return 'caught'
    def default_exc_view(request):
        calls.append('default')
        return 'default'
    config.add_view(bad_view)
    config.add_exception_view(default_exc_view, renderer='string')
    config.add_exception_view(
        retryable_exc_view, retryable_error=True, renderer='string')
    app = config.make_wsgi_app()
    app = webtest.TestApp(app)
    response = app.get('/')
    assert response.body == b'default'
    assert calls == ['fail', 'caught', 'fail', 'caught', 'fail', 'default']


def test_retryable_exception_is_ignored_on_last_attempt(config):
    from pyramid_retry import RetryableException
    calls = []
    def bad_view(request):
        calls.append('fail')
        raise RetryableException
    config.add_view(bad_view)
    app = config.make_wsgi_app()
    app = webtest.TestApp(app)
    with pytest.raises(Exception):
        app.get('/')
    assert calls == ['fail', 'fail', 'fail']


def test_BeforeRetry_event_is_raised(config):
    from pyramid_retry import RetryableException
    from pyramid_retry import IBeforeRetry
    calls = []
    retries = []
    def retry_subscriber(event):
        retries.append(event)
    def final_view(request):
        calls.append('ok')
        return 'ok'
    def bad_view(request):
        calls.append('fail')
        raise RetryableException
    config.add_subscriber(retry_subscriber, IBeforeRetry)
    config.add_view(bad_view, last_retry_attempt=False)
    config.add_view(final_view, last_retry_attempt=True, renderer='string')
    app = config.make_wsgi_app()
    app = webtest.TestApp(app)
    response = app.get('/')
    assert response.body == b'ok'
    assert calls == ['fail', 'fail', 'ok']
    assert len(retries) == 2


def test_BeforeRetry_event_is_raised_from_squashed_exception(config):
    from pyramid_retry import IBeforeRetry
    from pyramid_retry import RetryableException
    calls = []
    retries = []
    def retry_subscriber(event):
        retries.append(event)
    def final_view(request):
        calls.append('ok')
        return 'ok'
    def bad_view(request):
        raise RetryableException
    def exc_view(request):
        calls.append('squash')
        return 'squash'
    config.add_subscriber(retry_subscriber, IBeforeRetry)
    config.add_view(bad_view, last_retry_attempt=False)
    config.add_view(exc_view, context=RetryableException, exception_only=True,
                    renderer='string')
    config.add_view(final_view, last_retry_attempt=True, renderer='string')
    app = config.make_wsgi_app()
    app = webtest.TestApp(app)
    response = app.get('/')
    assert response.body == b'ok'
    assert calls == ['squash', 'squash', 'ok']
    assert len(retries) == 2


def test_activate_hook_overrides_default_attempts(config):
    from pyramid_retry import RetryableException
    calls = []
    def activate_hook(request):
        return 1
    def bad_view(request):
        calls.append('fail')
        raise RetryableException
    config.add_settings({
        'retry.attempts': 3,
        'retry.activate_hook': activate_hook,
    })
    config.add_view(bad_view)
    app = config.make_wsgi_app()
    app = webtest.TestApp(app)
    with pytest.raises(Exception):
        app.get('/')
    assert calls == ['fail']


def test_activate_hook_falls_back_to_default_attempts(config):
    from pyramid_retry import RetryableException
    calls = []
    def activate_hook(request):
        return None
    def bad_view(request):
        calls.append('fail')
        raise RetryableException
    config.add_settings({
        'retry.attempts': 3,
        'retry.activate_hook': activate_hook,
    })
    config.add_view(bad_view)
    app = config.make_wsgi_app()
    app = webtest.TestApp(app)
    with pytest.raises(Exception):
        app.get('/')
    assert calls == ['fail', 'fail', 'fail']


def test_is_last_attempt_True_when_inactive():
    from pyramid_retry import is_last_attempt
    request = pyramid.request.Request.blank('/')
    assert is_last_attempt(request)


def test_retryable_error_predicate_is_bool(config):
    from pyramid.exceptions import ConfigurationError
    view = lambda r: 'ok'
    with pytest.raises(ConfigurationError):
        config.add_view(view, retryable_error='yes', renderer='string')
        config.commit()


def test_last_retry_attempt_predicate_is_bool(config):
    from pyramid.exceptions import ConfigurationError
    view = lambda r: 'ok'
    with pytest.raises(ConfigurationError):
        config.add_view(view, last_retry_attempt='yes', renderer='string')
        config.commit()

def test_mark_error_retryable_on_non_error():
    from pyramid_retry import mark_error_retryable
    with pytest.raises(ValueError):
        mark_error_retryable('some string')
