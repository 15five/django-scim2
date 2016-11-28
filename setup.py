#!/usr/bin/env python
# Installs django_scim.

from setuptools import setup
import os
import sys
import unittest


def long_description():
    """Get the long description from the README"""
    return open(os.path.join(sys.path[0], 'README.rst')).read()

def run_tests():
    test_loader = unittest.TestLoader()
    return test_loader.discover('django_scim', pattern='test_*.py')


setup(
    author='Erik van Zijst',
    author_email='erik.van.zijst@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    description='A partial implementation of the SCIM 2.0 provider specification for use with Django.',
    download_url='https://bitbucket.org/atlassian/django_scim/downloads/django_scim-0.4.1.tar.gz',
    keywords='django scim',
    license='MIT',
    long_description=long_description(),
    name='django_scim',
    packages=['django_scim'],
    install_requires=[
        'python-dateutil==2.6.0',
        'PlyPlus-ff==0.7.2b1',
    ],
    scripts=['scim'],
    url='https://bitbucket.org/atlassian/django_scim',
    version='0.4.1',
    test_suite='setup.run_tests',
)

