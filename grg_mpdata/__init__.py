"""a package for reading and writing of matpower data files"""

import pkg_resources
__version__ = pkg_resources.require('grg_mpdata')[0].version

# import standard entry points to the code
from grg_mpdata import io
from grg_mpdata import exception
from grg_mpdata import cmd
