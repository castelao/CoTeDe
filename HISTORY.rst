.. :changelog:

History
=======

0.20 - Jul, 2018
----------------

* Removing dependency on pyArgo and pySeabird. Generalizing CoTeDe for other uses, thus now on PyArgo, PySeabird, and other packages to come public soon that use CoTeDe.

0.19
----------------

* CARS features and flags

0.17 - Mar, 2016
----------------

* Implementing fuzzy procedures inside CoTeDe, thus removing dependency on scikit-fuzzy. scikit-fuzzy is broken, hence compromising tests and development of CoTeDe.

0.16 - Mar, 2016
----------------

* Using external package OceansDB to handle climatologies and bathymetry.

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

* Following CF vocabulary for variables names (PRES, TEMP, PSAL...)
* Partial support to ARGO profiles
* Added density invertion test
* Included haversine to avoid dependency on MAUD.
* tox and travis support.

0.9 - Dec, 2013
---------------

* Going public

0.7.3
-----

* Creating fProfileQC()

0.5.4 - Nov, 2013
-----------------

* Including Tukey53H test

0.5.0
-----

* Implemented ProfileQCCollection

0.4 - Sep, 2013
---------------

* gradient and spike tests with depth conditional thresholds
* CruiseQC
* Use default threshold values for the QC tests.

0.1 - May 24, 2013
------------------

* Initial release.

QC_ML - 2011
------------

* QC_ML, a machine learning approach to quality control hydrographic data, the initial prototype of CoTeDe. I refactored the system I developed to quality control TSG, to evaluate the PIRATA's CTD stations for INPE. At this point I migrated from my personal Subversion server to Bitbucket, and I lost the history and logs before this point.

2006
----

* A system to automaticaly quality control TSG data on realtime for AOML-NOAA. The data was handled in a PostgreSQL database, and only the traditional tests were applied, i.e. a sequence of binary tests (spike, gradient, valid position ...).
