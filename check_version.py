#!/usr/bin/env python

import subprocess
import grg_mpdata

git_version = subprocess.check_output(['git', 'describe', '--tags']).rstrip().decode('ascii')

py_version = grg_mpdata.__version__

print(git_version)
print(py_version)

