.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/Pylons/pyramid_retry/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "feature"
is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

pyramid_retry could always use more documentation, whether as part of the
official pyramid_retry docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at
https://github.com/Pylons/pyramid_retry/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `pyramid_retry` for local development.

1. Fork the `pyramid_retry` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/pyramid_retry.git

3. Install your local copy into a virtualenv::

    $ python3 -m venv env
    $ env/bin/pip install -e .[docs,testing]
    $ env/bin/pip install tox

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and
   the tests, including testing other Python versions with tox::

    $ env/bin/tox

6. Add your name to the ``CONTRIBUTORS.txt`` file in the root of the
   repository.

7. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

8. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 3.7 and up and for PyPy 3.8 and up.
4. When your pull request is posted, a maintainer will click the button to run
   Github Actions, afterwards validate that your PR is valid for all tested
   platforms/Python versions

Tips
----

To run a subset of tests::

$ env/bin/py.test tests.test_it
