=============
CoTe De l'eau
=============

This package is intended to quality control CTD stations by applying
a sequence of tests. It uses the Seabird package to interpret the
SeaBird's .cnv output file.

This is the result from several generations of quality control systems,
which started in 2006, while I was in charge of the quality control
of termosalinographs at AOML-NOAA, USA. Later I was advising the
quality control of the brazilian hydrography of PIRATA.

CoTeDe can apply different quality control procedures:
  - The default GTSPP or EGOOS procedure;
  - A custom set of tests and user defined thresholds;
  - A novel approach based on Anomaly Detection, described by `Castelao 2015 <http://arxiv.org/abs/1503.02714>`_;

Quick howto
___________

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


Check the notebooks galery for more examples and functionalities: http://nbviewer.ipython.org/github/castelao/CoTeDe/tree/master/docs/notebooks/

Support and Documentation
-------------------------

http://cotede.readthedocs.org/en/latest/

How I see quality control
-------------------------

Quality control is different then data processing. 
On the processed data, the quality control/quality assurance means to check what looks fine. 
It is very important that the data is properly sampled and processed. 
The quality control procedures can't go back on time and fix improper sampling, but only tell you that the data don't looks fine.

Why CoTeDe?
-----------

For a long time I had the idea of the anomaly detection technique in mind, but I only really formalize the procedure in 2013, when I spent few months in Toulouse. 
The full name of this package is CoTe De l'eau, which I understand as something near to "rating the water". 
The short name is cotede, to make easier for the users to remember, since it is the quality control of COnductivity TEmperature and DEpth (cotede). 
The french name is a kind of tribute to the great time that I spent in France with Bia and the croissants that were converted in code lines.

