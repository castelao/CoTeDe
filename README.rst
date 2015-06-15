=============
CoTe De l'eau
=============

.. image:: https://zenodo.org/badge/doi/10.5281/zenodo.18589.svg
   :target: http://dx.doi.org/10.5281/zenodo.18589


This package is intended to quality control temperature and salinity profiles by applying a sequence of tests. 
For CTD profiles it uses the `PySeabird package <http://seabird.castelao.net>`_, so it can interpret directly the SeaBird's .cnv output file.

This is the result from several generations of quality control systems,
which started in 2006, while I was applying the quality control
of termosalinographs at AOML-NOAA, USA. Later I was advising the
quality control of the brazilian hydrography of PIRATA.

Why use CoTeDe
--------------

CoTeDe can apply different quality control procedures:
  - The default GTSPP or EGOOS procedure;
  - A custom set of tests, including user defined thresholds;
  - A novel approach based on Anomaly Detection, described by `Castelao 2015 <http://arxiv.org/abs/1503.02714>`_;

Process multiple files in parallel, ideal for large datasets.

Export output, original data plus flags, into netCDF files following OCEANSites data structure.

Quick howto
___________

To evaluate the records of a profile:

        import cotede.qc

        pqc = cotede.qc.fProfileQC('example.cnv')

To see the temperature records of the primary sensor:

        pqc['temperature']

To see the flags of all tests applied on the secondary sensor of salinity:

        pqc.flags['salinity2']

To evaluate a full set of profiles at once, like all profiles from a cruise, use the class ProfileQCCollection, like:

        dataset = ProfileQCCollection('/path/to/data/', inputpattern=".*\.cnv")

        dataset.flags['temperature'].keys()

Check the notebooks galery for more examples and functionalities: http://nbviewer.ipython.org/github/castelao/CoTeDe/tree/master/docs/notebooks/

Documentation
-------------

http://cotede.readthedocs.org

Why the name CoTeDe?
--------------------

Since NOAA I wanted to combine the multiple tests, but I didn't really knew how  to do that. 
In 2011 I learned the anomaly detection technique, but I only formalize the procedure in 2013, when I spent few months in Toulouse. 
The full name of this package is CoTe De l'eau, which I understand as something near to "rating the water". 
The short name is cotede, to make easier for the users to remember, since it is the quality control of COnductivity TEmperature and DEpth (cotede). 
The french name is a kind of tribute to the great time that I spent in France with Bia and the croissants that were converted in code lines.

