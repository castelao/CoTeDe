*************************
Tests for Quality Control
*************************

These are the tests available, and can be explicity accessed at cotede.qctests. 
Most of them simply reproduce the procedure recommended by GTSPP, EuroGOOS, IMOS and others. 

Flag table

Tests

Valid Date

Valid Position

At Sea

Gradient

  This test compares

    .. math::

       X_i = \left| V_i - \frac{V_{i+1} + V_{i-1}}{2} \right|

Spike

.. math::

   X_i = \left| V_i - \frac{V_{i+1} + V_{i-1}}{2} \right| - \left| \frac{V_{i+1} - V_{i-1}}{2} \right|


Climatology

.. math::

    X_i = \frac{V_{it} - <V_t>}{\sigma}


Tests according to Instrument Type
----------------------------------

- CTD

- TSG

  1. Platform Identification
  2. Impossible Date
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

- XBT

- ARGO

References
