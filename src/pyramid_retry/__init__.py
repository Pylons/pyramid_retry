import inspect
from pyramid.config import PHASE1_CONFIG
from pyramid.exceptions import ConfigurationError
from pyramid.httpexceptions import HTTPNotFound
import sys
from zope.interface import (
    Attribute,
    Interface,
    alsoProvides,
    classImplements,
    implementer,
)

from .compat import reraise


class IRetryableError(Interface):
    """
    A marker interface for retryable errors.

    An interface can be applied to any ``Exception`` class or object to
    indicate that it should be treated as a :term:`retryable error`.

    """


class IBeforeRetry(Interface):
    """
    An event emitted immediately prior to throwing away the request
    and creating a new one.

    This event may be useful when state is stored on the ``request.environ``
    that needs to be updated before a new request is created.

    """
    environ = Attribute('The environ object that is reused between requests.')
    request = Attribute('The request object that is being discarded.')


@implementer(IBeforeRetry)
class BeforeRetry(object):
    """
    An event emitted immediately prior to throwing away the request
    and creating a new one.

    This event may be useful when state is stored on the ``request.environ``
    that needs to be updated before a new request is created.

    :ivar request: The :class:`pyramid.request.Request` object that is being
                   discarded.

    """
    def __init__(self, request):
        self.request = request
        self.environ = request.environ


@implementer(IRetryableError)
class RetryableException(Exception):
    """ A retryable exception should be raised when an error occurs."""


def RetryableExecutionPolicy(attempts=3, activate_hook=None):
    """
    Create a :term:`execution policy` that catches any
    :term:`retryable error` and sends it through the pipeline again up to
    a maximum of ``attempts`` attempts.

    If ``activate_hook`` is set it will be consulted prior to each request
    to determine if retries should be enabled. It should return a number > 0
    of attempts to be used or ``None`` which will indicate to use the default
    number of attempts.

    """
    assert attempts > 0

    def retry_policy(environ, router):
        # make the original request
        request = router.make_request(environ)

        if activate_hook:
            retry_attempts = activate_hook(request)
            if retry_attempts is None:
                retry_attempts = attempts
            else:
                assert retry_attempts > 0
        else:
            retry_attempts = attempts

        # if we are supporting multiple attempts then we must make
        # make the body seekable in order to re-use it across multiple
        # attempts. make_body_seekable will copy wsgi.input if
        # necessary, otherwise it will rewind the copy to position zero
        if retry_attempts != 1:
            request.make_body_seekable()

        for number in range(retry_attempts):
            # track the attempt info in the environ
            # try to set it as soon as possible so that it's available
            # in the request factory and elsewhere if people want it
            # note: set all of these values here as they are cleared after
            # each attempt
            environ['retry.attempt'] = number
            environ['retry.attempts'] = retry_attempts

            # if we are not on the first attempt then we should start
            # with a new request object and throw away any changes to
            # the old object, however we do this carefully to try and
            # avoid extra copies of the body
            if number > 0:
                # try to make sure this code stays in sync with pyramid's
                # router which normally creates requests
                request = router.make_request(environ)

            try:
                response = router.invoke_request(request)

                # check for a squashed exception and handle it
                # this would happen if an exception view was invoked and
                # rendered an error response
                exc = getattr(request, 'exception', None)
                if exc is not None:
                    # if this is a retryable exception then continue to the
                    # next attempt, discarding the current response
                    if is_error_retryable(request, exc):
                        request.registry.notify(BeforeRetry(request))
                        continue

                return response

            except Exception:
                exc_info = sys.exc_info()
                try:
                    # if this was the last attempt or the exception is not
                    # retryable then make a last ditch effort to render an
                    # error response before sending the exception up the stack
                    if not is_error_retryable(request, exc_info[1]):
                        try:
                            return request.invoke_exception_view(exc_info)
                        except HTTPNotFound:
                            reraise(*exc_info)

                    else:
                        request.registry.notify(BeforeRetry(request))

                finally:
                    del exc_info  # avoid leak

            # cleanup any changes we made to the request
            finally:
                del environ['retry.attempt']
                del environ['retry.attempts']

    return retry_policy


def mark_error_retryable(error):
    """
    Mark an exception instance or type as retryable. If this exception
    is caught by ``pyramid_retry`` then it may retry the request.

    """
    if isinstance(error, Exception):
        alsoProvides(error, IRetryableError)
    elif inspect.isclass(error) and issubclass(error, Exception):
        classImplements(error, IRetryableError)
    else:
        raise ValueError(
            'only exception objects or types may be marked retryable')


def is_error_retryable(request, exc):
    """
    Return ``True`` if the exception is recognized as :term:`retryable error`.

    This will return ``False`` if the request is on its last attempt.
    This will return ``False`` if ``pyramid_retry`` is inactive for the
    request.

    """
    if is_last_attempt(request):
        return False

    return (
        isinstance(exc, RetryableException)
        or IRetryableError.providedBy(exc)
    )


def is_last_attempt(request):
    """
    Return ``True`` if the request is on its last attempt, meaning that
    ``pyramid_retry`` will not be issuing any new attempts, regardless of
    what happens when executing this request.

    This will return ``True`` if ``pyramid_retry`` is inactive for the
    request.

    """
    environ = request.environ
    attempt = environ.get('retry.attempt')
    attempts = environ.get('retry.attempts')
    if attempt is None or attempts is None:
        return True

    return attempt + 1 == attempts


class RetryableErrorPredicate(object):
    """
    A :term:`view predicate` registered as ``retryable_error``. Can be
    used to determine if an exception view should execute based on whether
    the exception is a :term:`retryable error`.

    .. seealso:: See :func:`pyramid_retry.is_error_retryable`.

    """
    def __init__(self, val, config):
        if not isinstance(val, bool):
            raise ConfigurationError(
                'The "retryable_error" view predicate value must be '
                'True or False.',
            )
        self.val = val

    def text(self):
        return 'retryable_error = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        exc = getattr(request, 'exception', None)
        is_retryable = is_error_retryable(request, exc)
        return (
            (self.val and is_retryable)
            or (not self.val and not is_retryable)
        )


class LastAttemptPredicate(object):
    """
    A :term:`view predicate` registered as ``last_retry_attempt``. Can be used
    to determine if an exception view should execute based on whether it's
    the last retry attempt before aborting the request.

    .. seealso:: See :func:`pyramid_retry.is_last_attempt`.

    """
    def __init__(self, val, config):
        if not isinstance(val, bool):
            raise ConfigurationError(
                'The "last_retry_attempt" view predicate value must be '
                'True or False.',
            )
        self.val = val

    def text(self):
        return 'last_retry_attempt = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        is_last = is_last_attempt(request)
        return ((self.val and is_last) or (not self.val and not is_last))


def includeme(config):
    """
    Activate the ``pyramid_retry`` execution policy in your application.

    This will add the :func:`pyramid_retry.RetryableErrorPolicy` with
    ``attempts`` pulled from the ``retry.attempts`` setting.

    The ``last_retry_attempt`` and ``retryable_error`` view predicates
    are registered.

    This should be included in your Pyramid application via
    ``config.include('pyramid_retry')``.

    """
    settings = config.get_settings()

    config.add_view_predicate('last_retry_attempt', LastAttemptPredicate)
    config.add_view_predicate('retryable_error', RetryableErrorPredicate)

    def register():
        attempts = int(settings.get('retry.attempts') or 3)
        settings['retry.attempts'] = attempts

        activate_hook = settings.get('retry.activate_hook')
        activate_hook = config.maybe_dotted(activate_hook)

        policy = RetryableExecutionPolicy(
            attempts,
            activate_hook=activate_hook,
        )
        config.set_execution_policy(policy)

    # defer registration to allow time to modify settings
    config.action(None, register, order=PHASE1_CONFIG)
