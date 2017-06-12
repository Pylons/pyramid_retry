from setuptools import setup, find_packages

def readfile(name):
    with open(name) as f:
        return f.read()

readme = readfile('README.rst')
changes = readfile('CHANGES.rst')

install_requires = [
    'pyramid >= 1.9.dev0',
    'zope.interface',
]

docs_require = [
    'Sphinx',
    'pylons-sphinx-themes',
    'repoze.sphinx.autointerface',
]

tests_require = [
    'pytest',
    'pytest-cov',
    'WebTest',
]

setup(
    name='pyramid_retry',
    version='0.4',
    description=(
        'An execution policy for Pyramid that supports retrying requests '
        'after certain failure exceptions.'
    ),
    long_description=readme + '\n\n' + changes,
    author='Michael Merickel',
    author_email='pylons-discuss@googlegroups.com',
    url='https://github.com/Pylons/pyramid_retry',
    packages=find_packages('src', exclude=['tests']),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=install_requires,
    extras_require={
        'docs': docs_require,
        'testing': tests_require,
    },
    zip_safe=False,
    keywords='pyramid wsgi retry attempt',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pyramid',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
