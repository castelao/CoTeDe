*************************
Tests for Quality Control
*************************

These are the tests available in CoTeDe.
Most of the QC recommended guides follow simmilar procedures with small variations, as described below when relevant.

.. _test-valid-date:

Valid Date
~~~~~~~~~~

Check if there is a valid date and time associated with the measurement.

.. _Argo_valid_date:

For Argo, the year also must be later than 1997.

For underwater gliders, the year must be later than 1998.

.. _test-valid-position:

Valid Position
~~~~~~~~~~~~~~

Check if there is a valid position associated with the measurement.
It should have a latitude between -90 and 90, and a longitude between -180 and 360.

.. _GTSPP-valid-position:

GTSPP restricts the longitude range to between -180 and 180 degrees.

.. _Argo_valid_position:

.. _test-location-at-sea:

Location at Sea
~~~~~~~~~~~~~~~

Check if the position is at sea by using a bathymetry database.
If not specified, it is used ETOPO1, a bathymetry with resolution of 1 minute.
This test implies approval on :ref:`test-valid-position`.

.. _GTSPP-at-sea:

If the position is determined at sea, GTSPP also evaluates the sounding, if present, but that is redundant to the Sounding Test, so this part is neglected in CoTeDe.

.. _Argo_on_land:

.. _test-global-range:

Global Range
~~~~~~~~~~~~

This test evaluates if the measurement is a possible value in the ocean in normal conditions.
The thresholds used are extreme values, wide enough to accommodate all possible values and do not discard uncommon, but possible, conditions.

.. _test-regional-range:

Regional Range
~~~~~~~~~~~~~~

This test is equivalent to the :ref:`test-global-range` but with a horizontal domain where it is applicable. Good examples are the Mediterranean Sea and the Red Sea, where the feasible range is more restrictive than required for the Global Range.

Regional Range was first introduced in the GTSPP manual 1990.

.. note::

    This test requires the Python package
    `Shapely <https://github.com/Toblerity/Shapely>`_ to read a polygon
    geometry and evaluate which positions are within that domain.

.. _GTSPP-regional-range:

GTSPP also requires the maximum depth to be less than 5200m in the Mediterranean Sea, and less than 3500m in the Red Sea.

.. _test-profile-envelop:

Profile Envelop
~~~~~~~~~~~~~~~

This test is equivalent to the :ref:`test-global-range` but with a vertical domain where it is applicable, i.e. it defines the acceptable range per layer.
For instance, GTSPP defines that deeper than 1100m up to 3000m the acceptable temperature range is from -1.5C to 18C.

Profile Envelop was first introduced in the GTSPP manual 1990.

.. _test-gradient:

Gradient
~~~~~~~~

  This test compares

    .. math::

       X_i = \left| V_i - \frac{V_{i+1} + V_{i-1}}{2} \right|

.. _test-gradient-cond:

Gradient Depth Conditional
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _test-spike:

Spike
~~~~~

.. math::

   X_i = \left| V_i - \frac{V_{i+1} + V_{i-1}}{2} \right| - \left| \frac{V_{i+1} - V_{i-1}}{2} \right|

.. _test-spike-cond:

Spike Depth Conditional
~~~~~~~~~~~~~~~~~~~~~~~

.. _test-tukey53H:

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

.. _test-climatology:

Climatology
~~~~~~~~~~~

.. math::

    X_i = \frac{V_{it} - <V_t>}{\sigma}


.. _QARTOD_Clim:

QARTOD climatological test is based on range

.. _test-rate-of-change:

Rate of Change
~~~~~~~~~~~~~~

.. _QARTOD_RoC:

For QARTOD, the delta change is normalized by the standard deviation.

.. _test-density-inversion:

Density Inversion
~~~~~~~~~~~~~~~~~

This test looks for density inversions in the water column, i.e. higher density above lower density.

Since density inversion is unstable it is not expected to be observed in nature in normal conditions. Note that weak inversions migth be observed near the surface under special conditions of sea surface heat fluxes. Sometimes a small negative threshold is used.

Density Inversion was first introduced in the GTSPP manual 1990.

.. _test-constant-cluster:

Constant Cluster
~~~~~~~~~~~~~~~~



.. _Argo_stuck:

For Argo ...

This test evaluates a cluster of adjacent measurements that are identical or nearly-identical.
This was implemented in CoTeDe as a generalization of the tests: Constant Profile, Stuck Value, Flat Line.

The Constant Profile tests was first introduced in the GTSPP manual 1990.

.. _GTSPP_stuck:

GTSPP call it Constant Profile test, and requires the full profile to be identical 3 or more measurements.

.. _test-deepest-pressure:

Deepest Pressure
~~~~~~~~~~~~~~~~

Check for each measurement if the reference pressure (depth) is deeper than the operational limit for that sensor/platform. For instance, the Argo Solo-II operates up to 2000m while the Deep Solo goes up to 6000m. Measurements deeper than that suggest a bad vertical position.

Reference: Argo QC manual 2.9.1

.. _test-digit-rollover:

Digit Rollover
~~~~~~~~~~~~~~~

Every sensor has a limit of bits available to store the sample value, with this limit planned to cover the possible range.
A spurious value over the bit range would be recorded as the scale rollover, resulting in a misleading value inside the possible scale.
This test identifies extreme jumps on consecutive measurements, that are wider than expected, suggesting a rollover error.

The difference on consecutive measurements must be smaller or equal to the threshold to be approved.
