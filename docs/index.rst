=============
pyramid_retry
=============

``pyramid_retry`` is an execution policy for Pyramid that wraps requests and
can retry them a configurable number of times under certain "retryable" error
conditions before indicating a failure to the client.

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
of attempts per request. The default number of attempts is ``1``.

The policy will handle any requests that fail because the application
raised an instance of :class:`pyramid_retry.RetryableException` or another
exception implementing the :class:`pyramid_retry.IRetryableError` interface:

.. code-block:: python

   @view_config(route_name='home')
   def failing_view(request):
       raise RetryableException

   @view_config(route_name='home', last_retry_attempt=True, renderer='string')
   def recovery_view(request):
       return 'success'

In this example, assuming ``retry.attempts`` was set to ``3``, the
``failing_view`` would be executed twice and finally the ``recover_view``
would return ``success`` on the final attempt.

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
