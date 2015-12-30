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

- `NetCDF4 <https://pypi.python.org/pypi/netCDF4>`_, is strongly recommended, since it allows to export data into netCDF as well as to read data required for some tests.  With NetCDF4 the tests "at sea" and "climatology comparison" can run acessing local files, the fastest way to do it.

- `PyDap <http://pydap.org>`_, if you want to run the climatology test accessing the WOA data from an OpenDAP server, and no not installed NetCDF4, you will need to install PyDAP.

- `Matplotlib <http://matplotlib.org>`_, is a powerfull library for data visualization. It is required for the graphic tools, like the visual inspection and classification of the data.

.. note::

    Without netCDF4 nor PyDAP it is not possible to run "at sea" neither 
    "climatology comparison" tests.

Installing CoTeDe
==================

Using pip
---------

If you don't already have PIP running on your machine, first you need to `install pip <https://pip.pypa.io/en/stable/installing.html>`_, then you can run:::

    $ pip install cotede

Alternative
-----------

Might be a good idea to install without update the dependencies, like::

    $ pip install --no-deps cotede

.. note::

    The ``--no-deps`` flag is optional, but highly recommended if you already
    have Numpy installed, otherwise pip will sometimes try to "help" you
    by upgrading your Numpy installation, which may not always be desired.

Custom setup
============

The directory .cotederc is the default home directory for CoTeDe support files, including the user custom QC setup. 
To use another directory, one can set and environment variable COTEDE_DIR. 
For example, if you use bash you could include the following lines in your .barsh_profile::

export COTEDE_DIR='~/my/different/path'

Optional
========

Climatology and bathymetry
--------------------------

The climatology comparison test and the at sea test can run acessing a local file, which is probably the fastest way to do it.
To download the required files you can inside python run this::

   >>> from cotede.utils import supportdata
   >>> supportdata.download_supportdata()

That will create, if doesn't already exist, a directory in your home: ~/.cotederc/data, and place the required WOA09 and etopo5 files there.
That was it, you're ready to run cotede in place with any of the preset configurations. 
Remember to run this before leave the dock, while you still have cheap and fast access to the network.

Testing
=======

I maintain a suite of tests to check CoTeDe while I keep changing and improving the code. You can use it to test if everything runs as expected on your machine. For that, in the directory where is the source code you can simply run in the shell (i.e. outside Python)::

    $ python setup.py test
