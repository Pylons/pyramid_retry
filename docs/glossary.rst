.. _glossary:

Glossary
========

.. glossary::
   :sorted:

   Pyramid
      A `web framework <https://trypyramid.com/>`_.

   retryable error
      An exception indicating that a request failed due to a transient error
      which may succeed if tried again. Examples might include lock contention
      or a flaky network connection to a third party service.

      A retryable error is usually an exception that inherits from
      :class:`pyramid_retry.RetryableException` but may also be any other
      exception that implements the :class:`pyramid_retry.IRetryableError`
      interface.

   execution policy
      A hook in :term:`Pyramid` which can control the entire request lifecycle.

   view predicate
      A predicate in :term:`Pyramid` which can help determine which view
      should be executed for a given request. Many views may be registered
      for a similar url, query strings etc and all predicates must pass
      in order for the view to be considered.
