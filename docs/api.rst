========================
:mod:`pyramid_retry` API
========================

.. automodule:: pyramid_retry

  .. autofunction:: includeme

  .. autofunction:: RetryableExecutionPolicy

  .. autofunction:: is_error_retryable

  .. autofunction:: is_last_attempt

  .. autoclass:: LastAttemptPredicate
     :members:

  .. autoclass:: RetryableErrorPredicate
     :members:

  .. autoexception:: RetryableException
     :members:

  .. autointerface:: IRetryableError
