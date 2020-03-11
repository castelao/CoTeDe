***************************
Getting Started with CoTeDe
***************************

To quality control CTD or TSG, please check the package `pySeabird <https://github.com/castelao/seabird>`_.

Inside python
=============

First load the module

.. code-block:: python

    >>> import cotede

With a data object from a CTD as described in the Data Model section, we can run the QC

.. code-block:: python

    >>> pqc = cotede.ProfileQC(ds)

The keys() will give you the data loaded from the CTD, similar to the ds itself

.. code-block:: python

    >>> pqc.keys()

To see one of the variables listed on the previous step

.. code-block:: python

    >>> pqc['sea_water_temperature']

The flags are stored at pqc.flags and is a dictionary, being one item per variable evaluated. For example, to see the flags for the salinity instrument

.. code-block:: python

    >>> pqc.flags['sea_water_salinity']

or for a specific test

.. code-block:: python

    >>> pqc.flags['sea_water_salinity']['gradient']

The class cotede.ProfileQCed is equivalent to the cotede.ProfileQC, but it already masks the non approved data (flag > 2). It can also be used like

.. code-block:: python

    >>> p = cotede.ProfileQCed(data)
    >>> p['sea_water_temperature']

To choose which QC criteria to apply

.. code-block:: python

    >>> pqc = cotede.ProfileQC(ds, 'cotede')

or

.. code-block:: python

    >>> pqc = cotede.ProfileQC(ds, 'gtspp')

To define manually the test to apply

.. code-block:: python

    >>> pqc = cotede.ProfileQC(ds, {'sea_water_temperature': {'gradient': {'threshold': 6}}})

More examples
=============

I keep a notebooks collection of `practical examples to Quality Control CTD data <http://nbviewer.ipython.org/github/castelao/cotede/tree/master/docs/notebooks/>`_
.
If you have any suggestion, please let me know.
