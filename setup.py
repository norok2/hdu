"""
Setup instructions.

See: https://packaging.python.org/en/latest/distributing.html
"""

from setuptools import setup, find_packages
from codecs import open  # use a consistent encoding (in Python 2)
import os

cwd = os.path.realpath(os.path.dirname(__file__))

# get the long description from the README file
with open(os.path.join(cwd, 'README'), encoding='utf-8') as readme_file:
    long_description = readme_file.read()

setup(
    name='hdu',

    use_scm_version=True,
    setup_requires=['setuptools_scm'],

    description='Human-friendly summary of disk usage.',
    long_description=long_description,

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

    keywords='sample setuptools development',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    # py_modules=['hdu'],

    # https://packaging.python.org/en/latest/requirements.html
    # install_requires=['peppercorn'],
    #
    # extras_require={
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },

    # package_data={
    #     'sample': ['package_data.dat'],
    # },

    # data_files=[('my_data', ['data/data_file'])],

    entry_points={
        'console_scripts': [
            'sample=sample:main',
        ],
    },
)
