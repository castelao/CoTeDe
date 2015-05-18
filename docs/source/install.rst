************
Installation
************

Requirements
============

- `Python <http://www.python.org/>`_ 2.6 (>=2.6.5), 2.7, 3.1 or 3.2

- `Numpy <http://www.numpy.org>`_ (>=1.1)

- `PySeabird <http://seabird.castelao.net>`_  

Optional requirement
--------------------

- `NetCDF4 <https://pypi.python.org/pypi/netCDF4>`_, if you want to be able to export the data into netCDF files. The climatology test can be executed accessing a local netCDF4 WOA file, which requires netCDF4, or accessing an OpenDAP server using PyDAP (look next item).

- `PyDap <http://pydap.org>`_, if you want to run the climatology test accessing the WOA data from an OpenDAP server you will need to install PyDAP.

Installing CoTeDe
==================

Using pip
---------

First you need to `install pip <https://pip.pypa.io>`_, then you can run:

    pip install cotede

Alternative
-----------
    pip install --no-deps cotede

.. note::

    The ``--no-deps`` flag is optional, but highly recommended if you already
    have Numpy installed, otherwise pip will sometimes try to "help" you
    by upgrading your Numpy installation, which may not always be desired.
