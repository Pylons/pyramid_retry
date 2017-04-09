from pyramid.exceptions import ConfigurationError
from pyramid.httpexceptions import HTTPNotFound
import sys
from zope.interface import (
    Interface,
    implementer,
)

from .compat import reraise


class IRetryableError(Interface):
    """
    A marker interface for retryable errors.

    An interface can be applied to any ``Exception`` class or object to
    indicate that it should be treated as a :term:`retryable error`.

    """


@implementer(IRetryableError)
class RetryableException(Exception):
    """ A retryable exception should be raised when an error occurs."""


def RetryableExecutionPolicy(attempts=3):
    """
    Create a :term:`execution policy` that catches any
    :term:`retryable error` and sends it through the pipeline again up to
    a maximum of ``attempts`` attempts.

    """
    def retry_policy(environ, router):
        # make the original request
        request = router.make_request(environ)

        # if we are supporting multiple attempts then we must make
        # make the body seekable in order to re-use it across multiple
        # attempts. make_body_seekable will copy wsgi.input if
        # necessary, otherwise it will rewind the copy to position zero
        if attempts != 1:
            request.make_body_seekable()

        for number in range(attempts):
            # track the attempt info in the environ
            # try to set it as soon as possible so that it's available
            # in the request factory and elsewhere if people want it
            # note: set all of these values here as they are cleared after
            # each attempt
            environ['retry.attempt'] = number
            environ['retry.attempts'] = attempts

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

                finally:
                    del exc_info  # avoid leak

            # cleanup any changes we made to the request
            finally:
                del environ['retry.attempt']
                del environ['retry.attempts']

    return retry_policy


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

    .. seealso:: See :func:`pyramid_retry.is_exc_retryable`.

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

    attempts = int(settings.get('retry.attempts') or 3)
    settings['retry.attempts'] = attempts

    policy = RetryableExecutionPolicy(attempts)
    config.set_execution_policy(policy)

    config.add_view_predicate('last_retry_attempt', LastAttemptPredicate)
    config.add_view_predicate('retryable_error', RetryableErrorPredicate)
