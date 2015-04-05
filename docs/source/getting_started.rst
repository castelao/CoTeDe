****************************
Getting Started with Seabird
****************************

Inside python
=============

First load the module::

    >>> import cotede

Now you're able to load the CTD data::

    >>> pqc = cotede.qc.fProfileQC('example.cnv')

The keys() will give you the data loaded from the CTD, similar to the output from the seabird.fCNV::

    >>> pqc.keys()

To see one of the read variables listed on the previous step::

    >>> pqc['temperature']

The flags are stored at pqc.flags and is a dictionary, being one item per variable evaluated. For example, to see the flags for the secondary salinity instrument, just do::

    >>> pqc.flags['salinity2']

or for a specific test::

    >>> pqc.flags['salinity2']['gradient']

To evaluate a full set of profiles at once, use the class ProfileQCCollection, like:::

    >>> dataset = ProfileQCCollection('/path/to/data/', inputpattern=".*\.cnv")
    >>> dataset.flags['temperature'].keys()

The class cotede.qc.ProfileQCed is equivalent to the cotede.qc.ProfileQC, but it already mask the non approved data (flag != 1). Another it can also be used like:::

    >>> from seabird import cnv
    >>> data = cnv.fCNV('example.cnv')

    >>> import cotede.qc
    >>> ped = cotede.qc.ProfileQCed(data)

More examples
=============

I keep a notebooks collection of `practical examples to Quality Control CTD data <http://nbviewer.ipython.org/github/castelao/cotede/tree/master/docs/notebooks/>`_
.
If you have any suggestion, please let me know.
