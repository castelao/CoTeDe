*************************
Tests for Quality Control
*************************

These are the tests available, and can be explicity accessed at cotede.qctests. 
Most of them simply reproduce the procedure recommended by GTSPP, EuroGOOS, IMOS, ARGO and others.

Flag table

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


=====
Tests
=====

Valid Date
~~~~~~~~~~

Valid Position
~~~~~~~~~~~~~~

Location at Sea
~~~~~~~~~~~~~~~

Gradient
~~~~~~~~

  This test compares

    .. math::

       X_i = \left| V_i - \frac{V_{i+1} + V_{i-1}}{2} \right|

Spike
~~~~~

.. math::

   X_i = \left| V_i - \frac{V_{i+1} + V_{i-1}}{2} \right| - \left| \frac{V_{i+1} - V_{i-1}}{2} \right|


Climatology
~~~~~~~~~~~

.. math::

    X_i = \frac{V_{it} - <V_t>}{\sigma}


=========================
Quality Control procedure
=========================



CTD
~~~

GTSPP

+---------------+------------+--------+
| Test          |         Flag        |
+---------------+------------+--------+
|               | if succeed | if fail|
+===============+============+========+
| `Valid Date`_ |            |        |
+------+--------+------------+--------+
| `Gradient`_   |            |        |
+------+--------+------------+--------+

EuroGOOS

TSG
~~~

  1. Platform Identification
  2. `Valid Date`_
  3. Impossible Location
  4. Location at Sea
  5. Impossible Speed
  6. Global Ranges
  7. Regional Ranges
  8. Spike
  9. Constant Value
  10. Gradient
  11. Climatology
..  12. NCEP Weekly analysis
..  13. Buddy Check
..  14. Water Samples
..  15. Calibrations

XBT
~~~

ARGO
~~~~

  1. Platform Identification
  2. `Valid Date`_
  3. Impossible location test
  4. Position on land test
  5. Impossible speed test
  6. Global range test
  7. Regional range test
  8. Pressure increasing test
  9. Spike test
  10. Top an dbottom spike test: obsolete
  11. `Gradient`_
  12. Digit rollover test
  13. Stuck value test
  14. Density inversion
  15. Grey list
  16. Gross salinity or temperature sensor drift
  17. Visual QC
  18. Frozen profile test
  19. Deepest pressure test


==========
References
==========
