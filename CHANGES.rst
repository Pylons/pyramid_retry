- Add the ``mark_error_retryable`` function in order to easily mark
  certain errors as retryable for ``pyramid_retry`` to detect.
  See https://github.com/Pylons/pyramid_retry/pull/8

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
