#!/usr/bin/env python

import sys
import subprocess
import grg_mpdata

git_describe = subprocess.check_output(['git', 'describe', '--tags']).rstrip().decode('ascii')

py_version = grg_mpdata.__version__

print('git describe: {}'.format(git_describe))

git_version = git_describe.split('-')[0].strip('v')
print('git version: {}'.format(git_version))

print('grg_mpdata version: {}'.format(py_version))


if git_version != py_version:
    print('git and python versions do not match')
    sys.exit(1)
