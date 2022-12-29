=============
pyramid_retry
=============

.. image:: https://img.shields.io/pypi/v/pyramid_retry.svg
    :target: https://pypi.python.org/pypi/pyramid_retry

.. image:: https://github.com/Pylons/pyramid_retry/actions/workflows/ci-tests.yml/badge.svg?branch=main
    :target: https://github.com/Pylons/pyramid_retry/actions/workflows/ci-tests.yml?query=branch%3Amain

.. image:: https://readthedocs.org/projects/pyramid_retry/badge/?version=latest
    :target: https://readthedocs.org/projects/pyramid_retry/?badge=latest
    :alt: Documentation Status

``pyramid_retry`` is an execution policy for Pyramid that wraps requests and
can retry them a configurable number of times under certain "retryable" error
conditions before indicating a failure to the client.

See https://docs.pylonsproject.org/projects/pyramid-retry/en/latest/
or ``docs/index.rst`` in this distribution for detailed
documentation.
