************
Installation
************

Requirements
============

- `Python <http://www.python.org/>`_ 2.7, or >= 3.6

- `Numpy <http://www.numpy.org>`_ (>=1.11)

- `Scipy <https://www.scipy.org>`_ (>=0.18.0)

Optional requirement
--------------------

- `OceansDB <https://pypi.python.org/pypi/OceansDB>`_, is a database of climatologies and bathymetry of the oceans. It is a requirement for few tests like valid position at sea, climatology comparison, and others.

- `Matplotlib <http://matplotlib.org>`_, is a powerfull library for data visualization. It is required for the graphic tools, like the visual inspection and classification of the data.

Installing CoTeDe
==================

Using pip
---------

If you don't already have PIP running on your machine, first you need to `install pip <https://pip.pypa.io/en/stable/installing.html>`_, then you can run::

    $ pip install cotede

Alternative
-----------

It is possible to install the latest version directly from the oven, but like a good bread it might not taste as good as if you wait it to cool down::

    $ pip install git+https://github.com/castelao/CoTeDe.git

If you can, use the standard pip install as shown previously.

Custom setup
============

The directory .cotederc is the default home directory for CoTeDe support files, including the user custom QC setup. 
To use another directory, one can set and environment variable COTEDE_DIR. 
For example, if you use bash you could include the following lines in your .barsh_profile::

    $ export COTEDE_DIR='~/my/different/path'

Optional
========

Climatology and bathymetry
--------------------------

The climatology comparison test and the at sea test use the package OceansDB, which maintain local files with the climatologies and bathymetry. Those files are automatically downloaded on the first time that they are required, but you can force the download by executing::

   >>> import oceansdb; oceansdb.CARS()['sea_water_temperature']
   >>> import oceansdb; oceansdb.WOA()['sea_water_temperature']
   >>> import oceansdb; oceansdb.ETOPO()['topography']

That will create, if doesn't already exist, a directory in your home: ~/.config, and place the required WOA, CARS, and etopo1 files there.
That was it, you're ready to run cotede in place with any of the preset configurations. 
Remember to run this before leave the dock, while you still have cheap and fast access to the network.

Testing
=======

I maintain a suite of tests to check CoTeDe while I keep changing and improving the code. You can use it to test if everything runs as expected on your machine. For that, in the directory where is the source code you can run in the shell (i.e. outside Python)::

    $ python setup.py test
