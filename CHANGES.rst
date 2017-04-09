unreleased
==========

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
