.. :changelog:

History
=======

0.14 - Aug, 2015
----

* Interface for human calibration of anomaly detection
* Implemented fuzzy logic criteria

0.13 - July, 2015
----

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
