.. :changelog:

History
=======

0.20 - Jul, 2018
----------------

* Removing dependency on `pySeabird <https://github.com/castelao/seabird>`_ and pyArgo. 
  Inversion of roles to generalize CoTeDe for other uses. Before CoTeDe would depend on pySeabird, but now CoTeDe is an optional requirement for pySeabird to QC CTD and TSG.

0.19
----------------

* CARS features and flags

0.17 - Mar, 2016
----------------

* Implementing fuzzy procedures inside CoTeDe, thus removing dependency on scikit-fuzzy. scikit-fuzzy is broken, hence compromising tests and development of CoTeDe.

0.16 - Mar, 2016
----------------

* Using external package `OceansDB <https://github.com/castelao/oceansdb>`_ to handle climatologies and bathymetry.

0.15 - Dec, 2015
----------------

* Moved procedures to handle climatology to external standalone packages.

0.14 - Aug, 2015
----------------

* Interface for human calibration of anomaly detection
* Implemented fuzzy logic criteria

0.13 - July, 2015
-----------------

* Major improvements in the anomaly detection submodule
* Partial support to thermosalinographs (TSG)
* Working on WOA test to generalize for profiles and tracks
* Adding .json to default QC configuration filenames
* Moved load_cfg from qc to utils

0.12
----

Since 0.9 some of the most important changes.

* Following OceanSites vocabulary for variable names (PRES, TEMP, PSAL...)
* Partial support to Argo profiles
* Added density invertion test
* Included haversine to avoid dependency on MAUD.
* tox and travis support.

0.9 - Dec, 2013
---------------

* A few people already had access but at this point it went open publicly.

0.7.3
-----

* Creating fProfileQC()

0.5.4 - Nov, 2013
-----------------

* Including Tukey53H test

0.5.0
-----

* Implemented ProfileQCCollection (later moved to PySeabird).

0.4 - Sep, 2013
---------------

* Gradient and spike tests with depth conditional thresholds.
* CruiseQC (later replaced by ProfileQCCollection).
* Use default threshold values for the QC tests.

0.1 - May 24, 2013
------------------

* Renamed to CoTeDe. Another major refactoring.

QC_ML - 2011
------------

* Renamed to QC_ML, a machine learning approach to quality control hydrographic data, the initial prototype of Anomaly Detection approach. I refactored the system I developed to quality control TSG, to evaluate the PIRATA's CTD stations for INPE. At that point I migrated from my personal Subversion server to Bitbucket, and I lost the detailed history and logs before that. 

2008
----

* Modified to parse Seabird CTDs so that the .cnv files could be directly QCed.

2006
----

* A system to automaticaly quality control TSG data on realtime for AOML-NOAA. The data was handled in a PostgreSQL database, and only the traditional tests were applied, i.e. a sequence of binary tests (spike, gradient, valid position ...).
