*****************
Anomaly Detection
*****************

Anomaly Detection is based on the concept of describe the statistical behaivior of known good data, and than use this as a reference to identify bad data by uncommon characteristics.

===================
Some funcionalities
===================

rank_files()
~~~~~~~~~~~~

From a list of data files, analyze all and characterize each measurement by a series of features, like for example the gradient or the difference with the climatology. 
Than, rank all files based on how unexpected is each feature, i.e. a measurement with a spike too intense, or too different from the climatology would show up first.

rank_files(datadir, varname, cfg=None)

- datadir: root directory with the data to be evaluated
- varname: Variable to be evaluated, like TEMP
- cfg: Q.C. rule to be considered

Return a list of all files inside datadir ordered by the probablity of being all good data.

Calibrate Anomaly Detection
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Calibrate the parameters for anomaly detection to best reproduce a preset Q.C. rule (for example: GTSPP). 
Since the anomaly detection consider simultaneously several features together to make a final decision, it should achieve more consistent results. 
A measurement with several tests too close to the traditional Q.C. thresholds would be approved by the traditional approach, but would raise suspicious, or even fail, in the anomaly detection approach.

calibrate_anomaly_detection(datadir, varname, cfg=None)
