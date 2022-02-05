#!/usr/bin/env python
# Installs django-scim2

import os
import sys

from setuptools import find_packages, setup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def long_description():
    """Get the long description from the README"""
    return open(os.path.join(BASE_DIR, 'README.rst')).read()


def run_tests():
    os.environ['DJANGO_SETTINGS_MODULE'] = os.environ.get('DJANGO_SETTINGS_MODULE', 'test_settings')

    import django
    django.setup()
    from django.test.utils import get_runner
    from django.conf import settings

    # eg. TEST_FILTER=tests.test_views.UserTestCase.test_get_user_by_id
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
    version='0.17.1',
    description='A partial implementation of the SCIM 2.0 provider specification for use with Django.',
    url='https://github.com/15five/django-scim2',
    download_url='https://github.com/15five/django-scim2/archive/master.zip',
    maintainer='Paul Logston',
    maintainer_email='paul@15five.com',
    author='Paul Logston',
    author_email='paul@15five.com',
    keywords='django scim 2.0',
    license='MIT',
    long_description=long_description(),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'Django>=2.2',
        'python-dateutil>=2.7.3',
        'scim2-filter-parser==0.3.5',
    ],
    tests_require=[
        'mock',
        'Django>=2.2,<4',
    ],
    test_suite='setup.run_tests',
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
