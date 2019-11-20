***************************
Getting Started with CoTeDe
***************************

To quality control CTD or TSG, please check the package `pySeabird <https://seabird.castelao.net>`_.

Inside python
=============

First load the module::

    >>> import cotede

With a data object from a CTD as described in the Data Model section, we can run the QC::

    >>> pqc = cotede.ProfileQC(ds)

The keys() will give you the data loaded from the CTD, similar to the ds itself::

    >>> pqc.keys()

To see one of the variables listed on the previous step::

    >>> pqc['TEMP']

The flags are stored at pqc.flags and is a dictionary, being one item per variable evaluated. For example, to see the flags for the salinity instrument::

    >>> pqc.flags['PSAL']

or for a specific test::

    >>> pqc.flags['PSAL']['gradient']

The class cotede.ProfileQCed is equivalent to the cotede.ProfileQC, but it already masks the non approved data (flag > 2). It can also be used like:::

    >>> p = cotede.ProfileQCed(data)
    >>> p['TEMP']

To choose which QC criteria to apply::

    >>> pqc = cotede.ProfileQC(ds, 'cotede')

or::

    >>> pqc = cotede.ProfileQC(ds, 'gtspp')

To define manually the test to apply::

    >>> pqc = cotede.ProfileQC(ds, {'TEMP': {'gradient': {'threshold': 6}}})

More examples
=============

I keep a notebooks collection of `practical examples to Quality Control CTD data <http://nbviewer.ipython.org/github/castelao/cotede/tree/master/docs/notebooks/>`_
.
If you have any suggestion, please let me know.
