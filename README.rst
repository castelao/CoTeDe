=============
CoTe De l'eau
=============

.. image:: https://zenodo.org/badge/doi/10.5281/zenodo.18589.svg
   :target: http://dx.doi.org/10.5281/zenodo.18589

.. image:: https://readthedocs.org/projects/cotede/badge/?version=latest
   :target: https://readthedocs.org/projects/cotede/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/travis/castelao/CoTeDe.svg
        :target: https://travis-ci.org/castelao/CoTeDe

.. image:: https://img.shields.io/pypi/v/cotede.svg
        :target: https://pypi.python.org/pypi/cotede


`CoTeDe<http://cotede.castelao.net>`_ is an Open Source Python package to quality control (QC) hydrographic data such as temperature and salinity. 
It was designed to attend individual scientists as well as operational systems with large databases, reading the inputs from different formats and types of sensors, and processing those in parallel for high performance. 
To achieve that, CoTeDe is highly customizable, allowing the user to compose the desired set of tests, as well as the specific parameters of each test. 
Otherwise there are preset QC procedures conforming with GTSPP, EuroGOOS and ARGO recommendations. 
It is also implemented innovating approaches to QC like the Fuzzy Logic (Timms 2011, Morello 2014) and Anomaly Detection (Castelão 2015). 

At this point it is operational for profiles (CTD, XBT and Argo) and tracks (TSG). 
For CTD profiles and TSG time series it uses `PySeabird package <http://seabird.castelao.net>`_ to interpret directly the SeaBird's .cnv output file, and for argo it uses `PyARGO package <https://github.com/castelao/pyARGO>`_ to interpret the netCDF files.

This is the result from several generations of quality control systems,
which started in 2006, when I developed from scratch an automatic quality 
control system for realtime evaluation of thermosalinographs at AOML-NOAA, USA. 
Later I was advising the quality control of the brazilian hydrography of PIRATA.

My vision is that we can do better than we do today with more flexible classification techniques, which includes machine learning, to minimize the burden on manual expert QC improving the consistency, performance and reliability of the QC procedure for oceanographic data, especially for realtime operations.

Why use CoTeDe
--------------

CoTeDe can apply different quality control procedures:
  - The default GTSPP, EGOOS or Argo procedures;
  - A custom set of tests, including user defined thresholds;
  - A novel approach based on Anomaly Detection, described by `Castelao 2015 <http://arxiv.org/abs/1503.02714>`_;
  - Two different fuzzy logic approaches: as proposed by Timms 2011 & Morello 2014, and using usual defuzification by the bisector.

Process multiple files in parallel, ideal for large datasets.

Export output, original data plus flags, into netCDF files following OCEANSites data structure.

Quick howto
-----------

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

Check the notebooks gallery for more examples and functionalities: http://nbviewer.ipython.org/github/castelao/CoTeDe/tree/master/docs/notebooks/

Documentation
-------------

http://cotede.readthedocs.org
