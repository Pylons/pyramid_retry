=============
pyramid_retry
=============

``pyramid_retry`` is an execution policy for Pyramid that wraps requests and
can retry them a configurable number of times under certain "retryable" error
conditions before indicating a failure to the client.

.. warning:: This package will only work with Pyramid 1.9 and newer.

Installation
============

Stable release
--------------

To install pyramid_retry, run this command in your terminal:

.. code-block:: console

    $ pip install pyramid_retry

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for pyramid_retry can be downloaded from the `Github repo`_.

.. code-block:: console

    $ git clone https://github.com/Pylons/pyramid_retry.git

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ pip install -e .

.. _Github repo: https://github.com/Pylons/pyramid_retry

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
:func:`pyramid_retry.RetryableExecutionPolicy` as an :term:`execution policy`
in your application using the ``retry.attempts`` setting as the maximum number
of attempts per request. The default number of attempts is ``3``. This number
is configurable in your application's ``.ini`` file as follows:

.. code-block:: ini

    [app:main]
    # ...
    retry.attempts = 3

The policy will handle any requests that fail because the application
raised an instance of :class:`pyramid_retry.RetryableException` or another
exception implementing the :class:`pyramid_retry.IRetryableError` interface.

The below, very contrived example, shows conceptually what's going on when
a request is retried. The ``failing_view`` is executed initially and for
the final attempt the ``recovery_view`` is executed.

.. code-block:: python

   @view_config(route_name='home')
   def failing_view(request):
       raise RetryableException

   @view_config(route_name='home', is_last_attempt=True, renderer='string')
   def recovery_view(request):
       return 'success'

Of course you probably wouldn't write actual code that expects to fail like
this. More realistically you may use a library like pyramid_tm_ to translate
certain transactional errors marked as "transient" into retryable errors.

.. _pyramid_tm: http://docs.pylonsproject.org/projects/pyramid-tm/en/latest/

Custom Retryable Errors
-----------------------

The simple approach to marking errors as retryable is to simply catch the
error and raise a :class:`pyramid_retry.RetryableException` instead:

.. code-block:: python

   from pyramid_retry import RetryableException
   import requests

   def view(request):
       try:
           response = requests.get('https://www.google.com')
       except requests.Timeout:
           raise RetryableException

This will work but if this is the last attempt then the failed request will
not actually be retried and on top of that the original exception is lost.

A better approach is to preserve the original exception and simply mark it
as retryable using the :class:`pyramid_retry.IRetryableError` marker
interface:

.. code-block:: python

   from pyramid_retry import mark_error_retryable
   import requests
   import zope.interface

   # mark requests.Timeout errors as retryable
   mark_error_retryable(requests.Timeout)

   def view(request):
       response = requests.get('https://www.google.com')

Per-Request Attempts
--------------------

It may be desirable to override the attempts per-request. For example, if
one endpoint on the system cannot afford to make a copy of the request via
``request.make_body_seekable()`` then the activate hook can be used to
set ``attempts=`` on that endpoint.

.. code-block:: python

    def activate_hook(request):
        if request.path == '/upload':
            return 1  # disable retries on this endpoint

    config.add_settings({'retry.activate_hook': activate_hook})

The ``activate_hook`` should return a number ``>= 1`` or ``None``. If ``None``
then the policy will fallback to the ``retry.attempts`` setting.

View Predicates
---------------

When the library is included in your application it registers two new view
predicates which are especially useful on exception views to determine
when to handle certain errors.

``retryable_error=[True/False]`` will match the exception view
only if the exception is both an :term:`retryable error` **and** there
are remaining attempts in which the request would be retried. See
:class:`pyramid_retry.RetryableErrorPredicate` for more information.

``last_retry_attempt=[True/False]`` will match only if, when the view is
executed, there will not be another attempt for this request.
See :class:`pyramid_retry.LastAttemptPredicate` for more information.

Receiving Retry Notifications
-----------------------------

The :class:`pyramid_retry.IBeforeRetry` event can be subscribed to receive
a callback with the ``request`` and ``environ`` prior to the pipeline
being completely torn down. This can be very helpful if any state is stored
on the ``environ`` itself that needs to be reset prior to the retry attempt.

.. code-block:: python

    from pyramid.events import subscriber
    from pyramid_retry import IBeforeRetry

    @subscriber(IBeforeRetry)
    def retry_event(event):
        print('A retry is about to occur.')

Caveats
=======

- In order to guarantee that a request can be retried it must make the body
  seekable. This is done via ``request.make_body_seekable()``. Generally the
  body is loaded directly from ``environ['wsgi.input']`` which is controlled
  by the WSGI server. However to make the body seekable it is copied into a
  seekable wrapper. In some cases this can lead to a very large copy operation
  before the request is executed.

- ``pyramid_retry`` does not copy the ``environ`` or make any attempt to
  restore it to its original state before retrying a request. This means
  anything stored on the ``environ`` will persist across requests created for
  that ``environ``.

More Information
================

.. toctree::
   :maxdepth: 1

   api
   glossary
   contributing
   changes

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
