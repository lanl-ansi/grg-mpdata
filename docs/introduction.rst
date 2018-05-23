============
Introduction
============

Overview
------------------------

grg-mpdata is a minimalist python package to support the reading and writing of Matpower_ network data files.

The primary entry point of the library is :class:`grg_mpdata.io` module, which contains the methods for data input and output.


Installation
------------------------

Simply run::

    pip install grg-mpdata


Testing
------------------------

grg-mpdata is designed to be a library that supports other software.  
It is not immediately useful from the terminal.
However, you can test the parsing functionality from the command line with:: 

    python -m grg_mpdata.io <path to Matpower case file>

If this command is successful, you will see a simplified plain text version of the network data printed to the terminal.

.. _Matpower: http://www.pserc.cornell.edu/matpower/


Compatibility
------------------------

The following features of the Matpower_ 5.1 specification are not replicated in this library,

1. The following fields are not supported, 'A', 'l', 'u', 'H', 'Cw', 'N', 'fparm', 'z0', 'zl', 'zu'
2. The matrix columns are not extensible

