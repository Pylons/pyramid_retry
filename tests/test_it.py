import pyramid.request
import pyramid.response
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
    first_exception = RetryableException()
    second_exception = RetryableException()
    exceptions_to_be_raised = [first_exception, second_exception]
    def retry_subscriber(event):
        retries.append(event)
    def final_view(request):
        calls.append('ok')
        return 'ok'
    def bad_view(request):
        calls.append('fail')
        raise exceptions_to_be_raised.pop(0)
    config.add_subscriber(retry_subscriber, IBeforeRetry)
    config.add_view(bad_view, last_retry_attempt=False)
    config.add_view(final_view, last_retry_attempt=True, renderer='string')
    app = config.make_wsgi_app()
    app = webtest.TestApp(app)
    response = app.get('/')
    assert response.body == b'ok'
    assert calls == ['fail', 'fail', 'ok']
    assert len(retries) == 2
    assert retries[0].exception == first_exception
    assert retries[0].response is None
    assert retries[1].exception == second_exception
    assert retries[1].response is None


def test_BeforeRetry_event_is_raised_from_squashed_exception(config):
    from pyramid_retry import IBeforeRetry
    from pyramid_retry import RetryableException
    calls = []
    retries = []
    first_exception = RetryableException()
    second_exception = RetryableException()
    exceptions_to_be_raised = [first_exception, second_exception]
    def retry_subscriber(event):
        retries.append(event)
    def final_view(request):
        calls.append('ok')
        return 'ok'
    def bad_view(request):
        raise exceptions_to_be_raised.pop(0)
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
    assert retries[0].exception == first_exception
    assert isinstance(retries[0].response, pyramid.response.Response)
    assert retries[1].exception == second_exception
    assert isinstance(retries[1].response, pyramid.response.Response)


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


def test_request_make_body_seekable_cleans_up_on_exception(config):
    from pyramid.threadlocal import manager
    # Clear defaults.
    manager.pop()
    calls = []
    def ok_view(request):
        calls.append('ok')
        return 'ok'
    config.add_view(ok_view, renderer='string')
    app = config.make_wsgi_app()
    app = webtest.TestApp(app)
    with pytest.raises(Exception):
        # Content-length=1 and empty body causes
        # webob.request.DisconnectionError:
        # The client disconnected while sending the body
        # (1 more bytes were expected) when you call
        # request.make_body_seekable().
        app.get('/', headers={'Content-Length': '1'})
    # len(manager.stack) == 1 when you don't catch exception
    # from request.make_body_seekable() and clean up.
    assert len(manager.stack) == 0
    # Request never invoked because of exception.
    assert not calls


def test_activate_hook_cleans_up_on_exception(config):
    from pyramid_retry import RetryableException
    from pyramid.threadlocal import manager
    # Clear defaults.
    manager.pop()
    calls = []
    def activate_hook(request):
        raise Exception
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
    # len(manager.stack) == 1 when you don't catch exception
    # from activate_hook and clean up.
    assert len(manager.stack) == 0
    # Request never invoked because of exception.
    assert not calls


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
