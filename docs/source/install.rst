************
Installation
************

CoTeDe was intentionally kept simple, avoiding dependencies, but when inevitable it uses fundamental libraries. There are indeed many benefits from modern libraries like pandas and xarray (yes, CoTeDe is old), but the goal was to allow other applications to adopt CoTeDe with ease. The optional extras allows some expansion.

Requirements
============

- `Python <http://www.python.org/>`_ 2.7 or 3.X (recommended >=3.7)

- `Numpy <http://www.numpy.org>`_ (>=1.11)

- `Scipy <https://www.scipy.org>`_ (>=0.18.0)

Optional requirement
--------------------

- `GSW <https://github.com/TEOS-10/GSW-Python>`_: a Python implementation of the Thermodynamic Equation of Seawater 2010 (TEOS-10). It is used to derive variables like sea water density from pressure, temperature, and salinity.

- `OceansDB <https://pypi.python.org/pypi/OceansDB>`_: a database of climatologies and bathymetry of the oceans. It is a requirement for tests like valid position at sea, climatology comparison, and others.

- `Matplotlib <http://matplotlib.org>`_: a powerfull library for data visualization. It is required for the graphic tools, like the visual inspection and classification of the data.

Installing CoTeDe
==================

Virtual Environments
--------------------

You don't need to, but I strongly recommend to use `virtualenv <https://virtualenv.pypa.io/en/stable/>`_ or `conda <https://conda.io/en/latest/>`_.

Using pip
---------

If you don't already have PIP running on your machine, first you need to `install pip <https://pip.pypa.io/en/stable/installing.html>`_, then you can run::

    $ pip install cotede

Custom Install
--------------

To install with GSW support, which allows to estimate density on the fly, you can run::

    pip install cotede[GSW]

To install with OceansDB in order to be able to run climatology tests, you can run::

    pip install cotede[OceansDB]

To install multiple extras::

    pip install cotede[GSW,OceansDB]

Last night's version
------------------

It is possible to install the latest version directly from the oven but, like a good bread, it might not taste as good as if you wait it to cool down::

    $ pip install git+https://github.com/castelao/CoTeDe.git

If you can, use the standard pip install as shown previously.

Custom setup
============

The directory ~/.config/cotederc is the default home directory for CoTeDe support files, including the user custom QC setup.
To use another directory, one can set and environment variable COTEDE_DIR. 
For example, if you use bash you could include the following lines in your .barsh_profile::

    $ export COTEDE_DIR='~/my/different/path'

Optional
========

Climatology and bathymetry
--------------------------

The climatology comparison test and the at sea test use the package OceansDB, which maintains local files with the climatologies and bathymetry. Those files are automatically downloaded on the first time that they are required, but you can force the download by executing::

   >>> import oceansdb; oceansdb.CARS()['sea_water_temperature']
   >>> import oceansdb; oceansdb.WOA()['sea_water_temperature']
   >>> import oceansdb; oceansdb.ETOPO()['topography']

That will create, if it doesn't already exist, a directory in your home: ~/.config, and place the required WOA, CARS, and etopo files there.
That is it, you're ready to run cotede in place with any of the preset configurations. 
If you're going to a cruise, remember to run this before leave the dock, while you still have cheap and fast access to the network.
