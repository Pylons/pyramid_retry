2.1.1 (2020-03-21)
==================

- Ensure the threadlocals are properly popped if the ``activate_hook`` throws
  an error or the request body fails to read due to a client disconnect.
  See https://github.com/Pylons/pyramid_retry/pull/20

2.1 (2019-09-30)
================

- Add ``exception`` and ``response`` attributes to the
  ``pyramid_retry.IBeforeRetry`` event.
  See https://github.com/Pylons/pyramid_retry/pull/19

2.0 (2019-06-06)
================

- No longer call ``invoke_exception_view`` if the policy catches an exception.
  If on the last attempt or non-retryable then the exception will now bubble
  out of the app and into WSGI middleware.
  See https://github.com/Pylons/pyramid_retry/pull/17

1.0 (2018-10-18)
================

- Support Python 3.7.

- Update the version we require for Pyramid to a non-prerelease so that pip and
  other tools don't accidentally install pre-release software.
  See https://github.com/Pylons/pyramid_retry/pull/13

0.5 (2017-06-19)
================

- Update the policy to to track changes in Pyramid 1.9b1. This is an
  incompatible change and requires at least Pyramid 1.9b1.
  See https://github.com/Pylons/pyramid_retry/pull/11

0.4 (2017-06-12)
================

- Add the ``mark_error_retryable`` function in order to easily mark
  certain errors as retryable for ``pyramid_retry`` to detect.
  See https://github.com/Pylons/pyramid_retry/pull/8

- Add the ``IBeforeRetry`` event that can be subscribed to be notified
  when a retry is about to occur in order to perform cleanup on the
  ``environ``. See https://github.com/Pylons/pyramid_retry/pull/9

0.3 (2017-04-10)
================

- Support a ``retry.activate_hook`` setting which can return a per-request
  number of retries. See https://github.com/Pylons/pyramid_retry/pull/4

- Configuration is deferred so that settings may be changed after
  ``config.include('pyramid_retry')`` is invoked until the configurator
  is committed. See https://github.com/Pylons/pyramid_retry/pull/4

- Rename the view predicates to ``last_retry_attempt`` and
  ``retryable_error``. See https://github.com/Pylons/pyramid_retry/pull/3

- Rename ``pyramid_retry.is_exc_retryable`` to
  ``pyramid_retry.is_error_retryable``.
  See https://github.com/Pylons/pyramid_retry/pull/3

0.2 (2017-03-02)
================

- Change the default attempts to 3 instead of 1.

- Rename the view predicates to ``is_last_attempt`` and ``is_exc_retryable``.

- Drop support for the ``tm.attempts`` setting.

- The ``retry.attempts`` setting is always set now in
  ``registry.settings['retry.attempts']`` so that apps can inspect it.

0.1 (2017-03-01)
================

- Initial release.
