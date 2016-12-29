#!/usr/bin/env python
# Installs django-scim2

from setuptools import setup
import os
import sys
import unittest
import sys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_version():
    path = os.path.join(BASE_DIR, 'django_scim', '__init__.py')
    version_line = None
    with open(path) as fp:
        for line in fp:
            if line.startswith('__version__'):
                version_line = line
                break
    if not version_line:
        raise ValueError('Unable to find version line in __init__.py')

    version = version_line.split('=')[1].strip().strip("'")
    return version


def long_description():
    """Get the long description from the README"""
    return open(os.path.join(BASE_DIR, 'README.rst')).read()

def run_tests():
    settings_mod = os.environ.get('DJANGO_SETTINGS_MODULE', 'test_settings')
    os.environ['DJANGO_SETTINGS_MODULE'] = settings_mod

    import django
    django.setup()
    from django.test.utils import get_runner
    from django.conf import settings

    test_filter = os.environ.get('TEST_FILTER')
    test_labels = [test_filter] if test_filter else []

    test_runner = get_runner(settings)
    failures = test_runner(
        pattern='test_*.py',
        verbosity=1,
        interactive=True
    ).run_tests(test_labels)
    sys.exit(failures)


setup(
    name='django-scim2',
    version=get_version(),
    description='A partial implementation of the SCIM 2.0 provider specification for use with Django.',
    url='https://github.com/15five/django-scim2',
    download_url='https://github.com/15five/django-scim2/archive/master.zip',
    maintainer='Paul Logston',
    maintainer_email='paul@15five.com',
    author='Erik van Zijst',
    author_email='erik.van.zijst@gmail.com',
    keywords='django scim 2.0',
    license='MIT',
    long_description=long_description(),
    packages=['django_scim'],
    install_requires=[
        'python-dateutil>=2.6.0',
        'PlyPlus>=0.7.2',
    ],
    scripts=['scim'],
    test_suite='setup.run_tests',
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

