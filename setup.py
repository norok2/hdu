#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup instructions.

See: https://packaging.python.org/en/latest/distributing.html
"""

# ======================================================================
# :: Future Imports (for Python 2)
from __future__ import (
    division, absolute_import, print_function, unicode_literals, )

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
NAME = 'hdu'
VERSION_FILEPATH = os.path.join(NAME.lower(), '_version.py')
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

    def dummy_version():
        return '0.0.0.0'

    if version is None:
        try:
            from setuptools_scm import get_version
        except ImportError:
            get_version = dummy_version
        version = get_version()

    if not os.path.isfile(source_filepath):
        version_template = \
            '#!/usr/bin/env python3\n' \
            '# -*- coding: utf-8 -*-\n' \
            '"""Package version file."""\n' \
            '# This file is automatically generated by `fix_version()`' \
            ' in the setup script.\n' \
            '__version__ = \'{version}\'\n'.format(version=version)
        with open(source_filepath, 'wb') as io_file:
            io_file.write(version_template.encode('utf-8'))
    else:
        with open(source_filepath, 'rb') as io_file:
            source = io_file.read().decode('utf-8')
            source = re.sub(
                r"__version__ = '.*'",
                "__version__ = '{}'".format(version),
                source, flags=re.UNICODE)
        with open(source_filepath, 'wb') as io_file:
            io_file.write(source.encode('utf-8'))

    return version


# ======================================================================
# :: call the setup tool
setup(
    name=NAME,

    description='Human-friendly summary of disk usage.',
    long_description=LONG_DESCRIPTION_TEXT,

    # use_scm_version=True,
    version=fix_version(),

    url='https://github.com/norok2/' + NAME.lower(),

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

    setup_requires=[
        'setuptools',
        'setuptools_scm'
    ],

    extras_require={
        'blessed': 'blessed',
    },

    entry_points={
        'console_scripts': [
            'hdu=hdu.hdu:main',
        ],
    },
)
