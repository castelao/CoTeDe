*************************
Tests for Quality Control
*************************

An automatic quality control is typically a composition of checks, each one looking for a different aspect to identify bad measurements.
This section covers the concept of the available checks and some ways how those could be combined.

A description and references for each test are available in `Tests`_.
The result of each test is a flag ranking the quality of the data as described in `Flags`_.
Finally, most of the users will probably follow one of the recommended procedures (GTSPP, Argo, QARTOD ...) described in `Quality Control Procedures`_.
If you are not sure what to do, start with one of those QC procedures and later fine tune it for your needs.
The default procedure for CoTeDe is the result of my experience with the World Ocean Database.


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


=====
Tests
=====

These are the tests available in CoTeDe.
Most of the QC recommended guides follow simmilar procedures with small variations, as described below when relevant.


Valid Date
~~~~~~~~~~

Check if there is a valid date and time associated with the measurement.

.. _Argo_valid_date:

For Argo, the year also must be later than 1997.

Valid Position
~~~~~~~~~~~~~~

.. _Argo_valid_position:

Check if there is a valid position associated with the measurement. It should have a latitude between -90 and 90, and a longitude between -180 and 360.

Location at Sea
~~~~~~~~~~~~~~~

.. _Argo_on_land:

Check if the position is at sea, which is evaluated using ETOPO1, a bathymetry with resolution of 1 minute.
The point is considered at sea if the interpolated position has a negative vertical level.

This test implicitly requires the data to pass the `Valid Position`_ test.

Global Range
~~~~~~~~~~~~

This test evaluates if the measurement is a possible value in the ocean in normal conditions.
The thresholds used are extreme values, wide enough to accommodate all possible values and do not discard uncommon, but possible, conditions.

Regional Range
~~~~~~~~~~~~~~

The regional Range test is equivalent to the Global Range but has a domain where it is applicable. Good examples are the Mediterranean Sea and the Red Sea, where the feasible range is more restrictive than required for the Global Range.

This test requires the Python package Shapely to read a polygon geometry and evaluate which positions are within that domain.

Reference: Argo QC manual

Digit Rollover
~~~~~~~~~~~~~~~

Every sensor has a limit of bits available to store the sample value, with this limit planned to cover the possible range.
A spurious value over the bit range would be recorded as the scale rollover, resulting in a misleading value inside the possible scale.
This test identifies extreme jumps on consecutive measurements, that are wider than expected, suggesting a rollover error.

The difference on consecutive measurements must be smaller or equal to the threshold to be approved.

Gradient
~~~~~~~~

  This test compares

    .. math::

       X_i = \left| V_i - \frac{V_{i+1} + V_{i-1}}{2} \right|

Spike
~~~~~

.. math::

   X_i = \left| V_i - \frac{V_{i+1} + V_{i-1}}{2} \right| - \left| \frac{V_{i+1} - V_{i-1}}{2} \right|

Tukey 53H
~~~~~~~~~

This method to detect spikes is based on the procedure initially proposed by Goring & Nikora 2002 for Acoustic Doppler Velocimeters, and similar to the one adopted by Morello 2011.
It takes advantage of the robustness of the median to create a smoother data series, which is then compared with the observation.
This difference is normalized by the standard deviation of the observed data series after removing the large--scale variability.

For one individual measurement :math:`x_i`, where :math:`i` is the position of the observation, it is evaluated as follows:

1. :math:`x^{(1)}` is the median of the five points from :math:`x_{i-2}` to :math:`x_{i+2}`;
2. :math:`x^{(2)}` is the median of the three points from :math:`x^{(1)}_{i-1}` to :math:`x^{(1)}_{i+1}`;
3. :math:`x^{(3)}` is the defined by the Hanning smoothing filter:
        :math:`\frac{1}{4}\left( x^{(2)}_{i-1} +2x^{(2)}_{i} +x^{(2)}_{i+1} \right)`
4. :math:`x_i` is a spike if :math:`\frac{|x_i-x^{(3)}|}{\sigma} > k`, where :math:`\sigma` is the standard deviation of the lowpass filtered data.


The default behavior in CoTeDe is to flag 4 if the test yields values higher than :math:`k=1.5`, and flag 1 if it is lower.


Climatology
~~~~~~~~~~~

.. math::

    X_i = \frac{V_{it} - <V_t>}{\sigma}


.. _QARTOD_Clim:

QARTOD climatological test is based on range

Profile Envelop
~~~~~~~~~~~~~~~


Rate of Change
~~~~~~~~~~~~~~

.. _QARTOD_RoC:

For QARTOD, the delta change is normalized by the standard deviation.

Density Inversion
~~~~~~~~~~~~~~~~~

For QARTOD, falgs T, C, and SP observations.

Density Treshold (DT)

sigma_theta n-1 + DT > sigma_theta n

Constant Cluster
~~~~~~~~~~~~~~~~



.. _Argo_stuck:

For Argo ...

.. _QARTOD_flatLine:

For QARTOD ...

.. _TSG_constantValue:

For TSG ...

==========================
Quality Control Procedures
==========================


Although I slightly modified the names of some Q.C. test, the concept behind is still the same.
The goal was to normalize all tests to return True if the data is good and False if the data is bad. 
For example, Argo's manual define "Impossible Date Test", while here I call it "`Valid Date`_".


Profile
=======

GTSPP
~~~~~

+--------------------+------------+--------+-------------+----------+
| Test               |         Flag        |       Threshold        |
+--------------------+------------+--------+-------------+----------+
|                    | if succeed | if fail| Temperature | Salinity |
+====================+============+========+=============+==========+
|                    |            |        |                        |
+--------------------+------------+--------+-------------+----------+
| `Valid Date`_      |  1         | 4      |                        |
+--------------------+------------+--------+-------------+----------+
| `Valid Position`_  |  1         |        |                        |
+--------------------+------------+--------+-------------+----------+
| `Location at Sea`_ |  1         |        |                        |
+--------------------+------------+--------+-------------+----------+
| `Global Range`_    |  1         |        | -2 to 40 C  | 0 to 41  |
+--------------------+------------+--------+-------------+----------+
| `Gradient`_        |  1         | 4      | 10.0 C      | 5        |
+--------------------+------------+--------+-------------+----------+
| `Spike`_           |  1         |        | 2.0 C       | 0.3      |
+--------------------+------------+--------+-------------+----------+
| `Climatology`_     |  1         |        |                        |
+--------------------+------------+--------+-------------+----------+
| `Profile Envelop`_ |            |        |                        |
+--------------------+------------+--------+-------------+----------+


EuroGOOS
~~~~~~~~

+--------------------+------------+--------+-------------+----------+
| Test               |         Flag        |       Threshold        |
+--------------------+------------+--------+-------------+----------+
|                    | if succeed | if fail| Temperature | Salinity |
+====================+============+========+=============+==========+
| `Valid Date`_      |  1         | 4      |                        |
+--------------------+------------+--------+-------------+----------+
| `Valid Position`_  |  1         | 4      |                        |
+--------------------+------------+--------+-------------+----------+
| `Location at Sea`_ |  1         | 4      |                        |
+--------------------+------------+--------+-------------+----------+
| `Global Range`_    |  1         | 4      | -2.5 to 40  | 2 to 41  |
+--------------------+------------+--------+-------------+----------+
| `Digit Rollover`_  |  1         | 4      |  10.0 C     | 5        |
+--------------------+------------+--------+-------------+----------+
| Gradient Cond.     |  1         | 4      |             |          |
|  - < 500           |            |        | - 9.0 C     | - 1.5    |
|  - > 500           |            |        | - 3.0 C     | - 0.5    |
+--------------------+------------+--------+-------------+----------+
| Spike Cond.        |  1         | 4      |             |          |
+--------------------+------------+--------+-------------+----------+
| `Climatology`_     |  1         |        |                        |
+--------------------+------------+--------+-------------+----------+


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
| `Global range`_                                       |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| `Regional Range`_                                     |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| Pressure increasing test                              |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| `Spike`_                                              |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| Top an dbottom spike test: obsolete                   |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| `Gradient`_                                           |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| `Digit Rollover`_                                     |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| :ref:`Stuck value test <Argo_stuck>`                  |            |        |                        |
+-------------------------------------------------------+------------+--------+-------------+----------+
| `Density Inversion`_                                  |            |        |                        |
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

+--------------------+------------+--------+-------------+----------+
| Test               |         Flag        |       Threshold        |
+--------------------+------------+--------+-------------+----------+
|                    | if succeed | if fail| Temperature | Salinity |
+====================+============+========+=============+==========+
| `Valid Date`_      |  1         | 3      |                        |
+--------------------+------------+--------+-------------+----------+
| `Valid Position`_  |  1         | 3      |                        |
+--------------------+------------+--------+-------------+----------+
| `Location at Sea`_ |  1         | 3      |                        |
+--------------------+------------+--------+-------------+----------+
| `Global Range`_    |  1         |        | -2.5 to 40  | 2 to 41  |
+--------------------+------------+--------+-------------+----------+
| `Gradient`_        |  1         | 4      | 10.0 C      | 5        |
+--------------------+------------+--------+-------------+----------+
| `Spike`_           |  1         |        | 2.0 C       | 0.3      |
+--------------------+------------+--------+-------------+----------+
| `Climatology`_     |  1         |        |                        |
+--------------------+------------+--------+-------------+----------+


QARTOD
~~~~~~

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
| Gross Range                            |            |        |             |          |
+----------------------------------------+------------+--------+-------------+----------+
| :ref:`Climatological <QARTOD_Clim>`    |            |        |                        |
+----------------------------------------+------------+--------+-------------+----------+
| `Spike`_                               |            |        |             |          |
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
  2. `Valid Date`_
  3. Impossible Location
  4. `Location at Sea`_
  5. Impossible Speed
  6. `Global Range`_
  7. `Regional Range`_
  8. `Spike`_
  9. :ref:`Constant Value <TSG_constantValue>`
  10. `Gradient`_
  11. Climatology
  12. NCEP Weekly analysis
  13. Buddy Check
  14. Water Samples
  15. Calibrations

XBT
~~~

==========
References
==========
