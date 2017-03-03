=============
pyramid_retry
=============

.. image:: https://img.shields.io/pypi/v/pyramid_retry.svg
    :target: https://pypi.python.org/pypi/pyramid_retry

.. image:: https://img.shields.io/travis/Pylons/pyramid_retry.svg
    :target: https://travis-ci.org/Pylons/pyramid_retry

.. image:: https://readthedocs.org/projects/pyramid_retry/badge/?version=latest
    :target: https://readthedocs.org/projects/pyramid_retry/?badge=latest
    :alt: Documentation Status

``pyramid_retry`` is an execution policy for Pyramid that wraps requests and
can retry them a configurable number of times under certain "retryable" error
conditions before indicating a failure to the client.

Usage
=====

Activate ``pyramid_retry`` by including it in your application:

.. code-block:: python

   def main(global_config, **settings):
       config = Configurator(settings=settings)
       config.include('pyramid_retry')
       # ...
       config.add_route('home', '/')

By default ``pyramid_retry`` will register an instance of
``pyramid_retry.RetryableExecutionPolicy`` as an execution policy in your
application using the ``retry.attempts`` setting as the maximum number of
attempts per request. The default number of attempts is ``3``.

The policy will handle any requests that fail because the application
raised an instance of ``pyramid_retry.RetryableException`` or another
exception implementing the ``pyramid_retry.IRetryableError`` interface:

.. code-block:: python

   @view_config(route_name='home')
   def failing_view(request):
       raise RetryableException

   @view_config(route_name='home', is_last_attempt=True, renderer='string')
   def recovery_view(request):
       return 'success'

In this example, assuming ``retry.attempts`` was set to ``3``, the
``failing_view`` would be executed twice and finally the ``recover_view``
would return ``success`` on the final attempt.
