#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup instructions.

See: https://packaging.python.org/en/latest/distributing.html
"""

from setuptools import setup, find_packages
from codecs import open  # use a consistent encoding (in Python 2)
import os  # Miscellaneous operating system interfaces
import re  # Regular expression operations

cwd = os.path.realpath(os.path.dirname(__file__))

# get the long description from the README file
with open(os.path.join(cwd, 'README'), encoding='utf-8') as readme_file:
    long_description_text = readme_file.read()


# ======================================================================
def fix_version(
        version=None,
        source_filepath='hdu/hdu.py'):
    if version is None:
        import setuptools_scm

        version = setuptools_scm.get_version(
            version_scheme='post-release',
            local_scheme='node-and-date'
        )
    with open(source_filepath, 'r+') as src_file:
        src_str = src_file.read()
        src_str = re.sub(
            r"__version__ \= '.*'",
            "__version__ = '{}'".format(version),
            src_str)
        src_file.seek(0)
        src_file.write(src_str + '\0')
    return version


version_text = fix_version()

# ======================================================================
setup(
    name='hdu',

    description='Human-friendly summary of disk usage.',
    long_description=long_description_text,

    # use_scm_version=True,
    version=version_text,

    url='https://bitbucket.org/norok2/hdu',

    author='Riccardo Metere',
    author_email='rick@metere.it',

    license='GPLv3+',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: System Administrators',

        'Topic :: System :: Shells',
        'Topic :: System :: Systems Administration',
        'Topic :: System :: Filesystems',
        'Topic :: System :: Monitoring',
        'Topic :: Utilities',

        'Operating System :: POSIX',

        'License :: OSI Approved :: GNU General Public License v3 or later'
        ' (GPLv3+)',

        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='hdu du disk usage console cli tui',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # package_data={
    #     'license': ['LICENSE'],
    # },

    # data_files=[('my_data', ['data/data_file'])],

    entry_points={
        'console_scripts': [
            'hdu=hdu.hdu:main',
        ],
    },

    setup_requires=['setuptools_scm'],
)
