*************************
Tests for Quality Control
*************************

An automatic quality control is typically a composition of checks, each one looking for a different aspect to identify bad measurements.
This section covers the concept of the available checks and some ways how those could be combined.

A description and references for each test are available in :ref:`qctests`.
The result of each test is a flag ranking the quality of the data as described in :ref:`flags`.
Finally, most of the users will probably follow one of the recommended procedures (GTSPP, Argo, QARTOD ...) described in `Quality Control Procedures`_.
If you are not sure what to do, start with one of those QC procedures and later fine tune it for your needs.
The default procedure for CoTeDe is the result of my experience with the World Ocean Database.

.. _flags:

=====
Flags
=====

The outcome of the QC evaluation is encoded following the IOC recommendation given in the table below
For example, if the climatology database is not available, the output flag would be 0, while a fail on the same climatology test would return a flag 3, if following the `GTSPP`_ recommendations.
By the end of all checks, each measurement receives an overall flag that is equal to the highest flag among all tests applied. Therefore, one mesurement with flag 0 was not evaluated at all, while a measurement with overall flag 4 means that at least one check considered that a bad data.

====    =======
Flag    Meaning
====    =======
0       No QC was performed
1       Good data
2       Probably good data
3       Probably bad data
4       Bad data
9       Missing data
====    =======

The flags 2 and 3 usually cause some confusion: "What do you mean by probably good or bad?"
The idea is to allow some choice for the final user.
The process of defining the criteria for any QC test is a duel between minimizing false positives or false negatives, thus it is a choice: What is more important for you?
There is no unique answer for all cases.
Most of the users will use anything greater than 2 as non-valid measurements.
Someone willing to pay the price of loosing more data to avoid by all means any bad data would rather discard anything greater than 1.
While someone more concerned in not wasting any data, even if that means a few mistakes, would discard anything greater than 3.
When designing a test or defining a new threshold, please assume that flag 4 is pretty confident that is a bad measurement.

It is typically expected to have one flag for each measurement in the dataset, but it is possible to have a situation with a single flag for the whole dataset.
For instance, if a profile is checked only for a valid geolocation, it would get a single flag for the whole profile.

Some procedures also provide a continuous scale usually representing the probablity of a measurement being good, like the Anomaly Detection and the Fuzzy Logic.
For details on that, please check the description of the specific check.


==========================
Quality Control Procedures
==========================


Although I slightly modified the names of some Q.C. test, the concept behind is still the same.
The goal was to normalize all tests to return True if the data is good and False if the data is bad. 
For example, Argo's manual define "Impossible Date Test", while here I call it ":ref:`test-valid-date`".


Profile
=======

GTSPP
~~~~~

+-----------------------------+------------+--------+-------------+----------+
| Test                        |         Flag        |       Threshold        |
+-----------------------------+------------+--------+-------------+----------+
|                             | if succeed | if fail| Temperature | Salinity |
+=============================+============+========+=============+==========+
| :ref:`test-valid-date`      |  1         | 4      |                        |
+-----------------------------+------------+--------+-------------+----------+
| :ref:`test-valid-position`  |  1         |        |                        |
+-----------------------------+------------+--------+-------------+----------+
| :ref:`test-location-at-sea` |  1         |        |                        |
+-----------------------------+------------+--------+-------------+----------+
| :ref:`test-global-range`    |  1         |        | -2 to 40 C  | 0 to 41  |
+-----------------------------+------------+--------+-------------+----------+
| :ref:`test-gradient`        |  1         | 4      | 10.0 C      | 5        |
+-----------------------------+------------+--------+-------------+----------+
| :ref:`test-spike`           |  1         |        | 2.0 C       | 0.3      |
+-----------------------------+------------+--------+-------------+----------+
| :ref:`test-climatology`     |  1         |        |                        |
+-----------------------------+------------+--------+-------------+----------+
| :ref:`test-profile-envelop` |            |        |                        |
+-----------------------------+------------+--------+-------------+----------+


EuroGOOS
~~~~~~~~

+-----------------------------+------------+--------+-------------+----------+
| Test                        |         Flag        |       Threshold        |
+-----------------------------+------------+--------+-------------+----------+
|                             | if succeed | if fail| Temperature | Salinity |
+=============================+============+========+=============+==========+
| :ref:`test-valid-date`      |  1         | 4      |                        |
+-----------------------------+------------+--------+-------------+----------+
| :ref:`test-valid-position`  |  1         | 4      |                        |
+-----------------------------+------------+--------+-------------+----------+
| :ref:`test-location-at-sea` |  1         | 4      |                        |
+-----------------------------+------------+--------+-------------+----------+
| :ref:`test-global-range`    |  1         | 4      | -2.5 to 40  | 2 to 41  |
+-----------------------------+------------+--------+-------------+----------+
| :ref:`test-digit-rollover`  |  1         | 4      |  10.0 C     | 5        |
+-----------------------------+------------+--------+-------------+----------+
| :ref:`test-gradient-cond`   |  1         | 4      |             |          |
|  - < 500                    |            |        | - 9.0 C     | - 1.5    |
|  - > 500                    |            |        | - 3.0 C     | - 0.5    |
+-----------------------------+------------+--------+-------------+----------+
| :ref:`test-spike-cond`      |  1         | 4      |             |          |
|  - < 500                    |            |        | - 6.0 C     | - 0.9    |
|  - > 500                    |            |        | - 2.0 C     | - 0.3    |
+-----------------------------+------------+--------+-------------+----------+
| :ref:`test-climatology`     |  1         |        |                        |
+-----------------------------+------------+--------+-------------+----------+


Argo (Incomplete)
~~~~~~~~~~~~~~~~~


+-------------------------------------------------------+------------+--------+-------------+----------+
| Test                                                  |         Flag        |       Threshold        |
+-------------------------------------------------------+------------+--------+-------------+----------+
|                                                       | if succeed | if fail| Temperature | Salinity |
+=======================================================+============+========+=============+==========+
| Platform Identification                               |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| :ref:`Valid Date <Argo_valid_date>`                   |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| :ref:`Impossible location test <Argo_valid_position>` |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| :ref:`Position on land test <Argo_on_land>`           |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| Impossible speed test                                 |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| :ref:`test-global-range`                              |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| :ref:`test-regional-range`                            |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| :ref:`Pressure increasing <Argo_increasing-pressure>` |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| :ref:`test-spike`                                     |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| Top an dbottom spike test: obsolete                   |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| :ref:`test-gradient`                                  |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| :ref:`test-digit-rollover`                            |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| :ref:`Stuck value test <Argo_stuck>`                  |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| :ref:`test-density-inversion`                         |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| Grey list                                             |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| Gross salinity or temperature sensor drift            |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| Visual QC                                             |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| Frozen profile test                                   |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| Deepest pressure test                                 |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+



IMOS (Incomplete)
~~~~~~~~~~~~~~~~~

+-----------------------------+------------+--------+-------------+----------+
| Test                        |         Flag        |       Threshold        |
+-----------------------------+------------+--------+-------------+----------+
|                             | if succeed | if fail| Temperature | Salinity |
+=============================+============+========+=============+==========+
| :ref:`test-valid-date`      |  1         | 3      |                        |
+-----------------------------+------------+--------+-------------+----------+
| :ref:`test-valid-position`  |  1         | 3      |                        |
+-----------------------------+------------+--------+-------------+----------+
| :ref:`test-location-at-sea` |  1         | 3      |                        |
+-----------------------------+------------+--------+-------------+----------+
| :ref:`test-global-range`    |  1         |        | -2.5 to 40  | 2 to 41  |
+-----------------------------+------------+--------+-------------+----------+
| :ref:`test-gradient`        |  1         | 4      | 10.0 C      | 5        |
+-----------------------------+------------+--------+-------------+----------+
| :ref:`test-spike`           |  1         |        | 2.0 C       | 0.3      |
+-----------------------------+------------+--------+-------------+----------+
| :ref:`test-climatology`     |  1         |        |                        |
+-----------------------------+------------+--------+-------------+----------+


QARTOD (Incomplete)
~~~~~~~~~~~~~~~~~~~

+----------------------------------------+------------+--------+-------------+----------+
| Test                                   |         Flag        |       Threshold        |
+----------------------------------------+------------+--------+-------------+----------+
|                                        | if succeed | if fail| Temperature | Salinity |
+========================================+============+========+=============+==========+
| Gap                                    |            |        |                        |
+----------------------------------------+------------+--------+-------------+----------+
| Syntax                                 |            |        |                        |
+----------------------------------------+------------+--------+-------------+----------+
| Location at Sea                        |            |        |                        |
+----------------------------------------+------------+--------+-------------+----------+
| :ref:`Gross Range <test-global-range>` |            |        |             |          |
+----------------------------------------+------------+--------+-------------+----------+
| :ref:`Climatological <QARTOD_Clim>`    |            |        |                        |
+----------------------------------------+------------+--------+-------------+----------+
| :ref:`test-spike`                      |            |        |             |          |
+----------------------------------------+------------+--------+-------------+----------+
| :ref:`Rate of Change <QARTOD_RoC>`     |            |    4   |             |          |
+----------------------------------------+------------+--------+-------------+----------+
| :ref:`Flat Line <QARTOD_flatLine>`     |            |        |             |          |
+----------------------------------------+------------+--------+-------------+----------+
| Multi-Variate                          |            |        |             |          |
+----------------------------------------+------------+--------+-------------+----------+
| Attenuated Signal                      |            |        |                        |
+----------------------------------------+------------+--------+-------------+----------+
| Neighbor                               |            |        |                        |
+----------------------------------------+------------+--------+-------------+----------+
| TS Curve Space                         |            |        |                        |
+----------------------------------------+------------+--------+-------------+----------+
|  Density Inversion                     |            |    3   |  0.03 kg/m3            |
+----------------------------------------+------------+--------+-------------+----------+


TSG
~~~

Based on AOML procedure. Realtime data is evaluatd by tests 1 to 10, while the delayed mode is evaluated by tests 1 to 15.

  1. Platform Identification
  2. :ref:`test-valid-date`
  3. Impossible Location
  4. `Location at Sea`_
  5. Impossible Speed
  6. `Global Range`_
  7. :ref:`test-regional-range`
  8. :ref:`test-spike`
  9. :ref:`Constant Value <TSG_constantValue>`
  10. :ref:`test-gradient`
  11. :ref:`test-climatology`
  12. NCEP Weekly analysis
  13. Buddy Check
  14. Water Samples
  15. Calibrations

XBT
~~~

==========
References
==========
