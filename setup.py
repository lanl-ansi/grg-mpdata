#from __future__ import print_function
import codecs
import os
import re

import subprocess

from setuptools import setup

def version():
    v = None
    try:
        v = subprocess.check_output(['git', 'describe', '--tags']).rstrip().decode('ascii')
    except:
        pass
    if v == None:
        v = subprocess.check_output(['git', '--git-dir', 'build/lanl-ansi/grg-mpdata/.git', 'describe', '--tags']).rstrip().decode('ascii')
    if '-' in v:
        v, ntag = v.split('-')[0:2]
        v = '{}-dev'.format(v)
    return v

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    long_description = readme.read()

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]

setup(
    name='grg-mpdata',
    packages=['grg_mpdata'],
    version=version(),
    url='https://github.com/lanl-ansi/grg-mpdata',
    license='BSD',

    author='Carleton Coffrin',
    author_email='cjc@lanl.gov',

    setup_requires=['pytest-runner'],
    tests_require=['pytest-cov'],
    test_suite='tests',
    description='Datastructures and methods for reading and writing Matpower data files',
    long_description=long_description,

    classifiers = classifiers,
)