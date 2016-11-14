#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup instructions.

See: https://packaging.python.org/en/latest/distributing.html
"""

# ======================================================================
# :: Future Imports (for Python 2)
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

# ======================================================================
# :: Python Standard Library Imports
import os  # Miscellaneous operating system interfaces
import re  # Regular expression operations
from codecs import open  # use a consistent encoding (in Python 2)

# ======================================================================
# :: Choice of the setup tools
from setuptools import setup
from setuptools import find_packages

# ======================================================================
# project specific variables
VERSION_FILEPATH = 'hdu/hdu.py'
README_FILEPATH = 'README.rst'

# get the working directory for the setup script
CWD = os.path.realpath(os.path.dirname(__file__))

# get the long description from the README file
with open(os.path.join(CWD, README_FILEPATH), encoding='utf-8') as readme_file:
    LONG_DESCRIPTION_TEXT = readme_file.read()


# ======================================================================
def fix_version(
        version=None,
        source_filepath=VERSION_FILEPATH):
    """
    Fix version in source code.

    Args:
        version (str): version to be used for fixing the source code
        source_filepath (str): Path to file where __version__ is located

    Returns:
        version (str): the actual version text used
    """
    if version is None:
        import setuptools_scm

        version = setuptools_scm.get_version()
    with open(source_filepath, 'r') as src_file:
        src_str = src_file.read()
        src_str = re.sub(
            r"__version__ = '.*'",
            "__version__ = '{}'".format(version),
            src_str)

    with open(source_filepath, 'w') as src_file:
        src_file.write(src_str)
    return version


version_text = fix_version()

# ======================================================================
# :: call the setup tool
setup(
    name='hdu',

    description='Human-friendly summary of disk usage.',
    long_description=LONG_DESCRIPTION_TEXT,

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
        'Programming Language :: Python :: 3',
    ],

    keywords=('hdu', 'du', 'disk', 'usage', 'console', 'cli', 'tui'),

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

    setup_requires=[
        'setuptools',
        'setuptools_scm'
    ],
)
