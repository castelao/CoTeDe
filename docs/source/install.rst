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

- `NetCDF4 <https://pypi.python.org/pypi/netCDF4>`_, is strongly recommended, since it allows to export data into netCDF as well as to read data required for some tests. With NetCDF4 the tests "at sea" and "climatology comparison" can run acessing local files, the fastest way to do it.

- `PyDap <http://pydap.org>`_, if you want to run the climatology test accessing the WOA data from an OpenDAP server, and no not installed NetCDF4, you will need to install PyDAP.

Installing CoTeDe
==================

Using pip
---------

If you don't already have PIP running on your machine, first you need to `install pip <https://pip.pypa.io/en/stable/installing.html>`_, then you can run:

    pip install cotede

Alternative
-----------
    pip install --no-deps cotede

.. note::

    The ``--no-deps`` flag is optional, but highly recommended if you already
    have Numpy installed, otherwise pip will sometimes try to "help" you
    by upgrading your Numpy installation, which may not always be desired.

Climatology and bathymetry datasets
-----------------------------------

The climatology comparison test and the at sea test can run acessing a local file, which is probably the fastest way to do it.
To download the required files you can inside python run this::

   >>> from cotede.utils import supportdata
   >>> supportdata.download_supportdata()

That will create, if doesn't already exist, a directory in your home: ~/.cotederc/data, and place the required WOA09 and etopo5 files there.
That was it, you're ready to run cotede with any of the preset configuration.
