======
CoTeDe
======

.. image:: https://zenodo.org/badge/10284681.svg
   :target: https://zenodo.org/badge/latestdoi/10284681

.. image:: https://readthedocs.org/projects/cotede/badge/?version=latest
   :target: https://readthedocs.org/projects/cotede/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/travis/castelao/CoTeDe.svg
   :target: https://travis-ci.org/castelao/CoTeDe

.. image:: https://codecov.io/gh/castelao/CoTeDe/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/castelao/CoTeDe

.. image:: https://img.shields.io/pypi/v/cotede.svg
   :target: https://pypi.python.org/pypi/cotede

.. image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/castelao/CoTeDe/master?filepath=docs%2Fnotebooks


`CoTeDe <http://cotede.castelao.net>`_ is an Open Source Python package to quality control (QC) oceanographic data such as temperature and salinity.
It was designed to attend individual scientists as well as real-time operations on large data centers.
To achieve that, CoTeDe is highly customizable, giving the user full control to compose the desired set of tests including the specific parameters of each test, or choose from a list of preset QC procedures.

I believe that we can do better than we have been doing with more flexible classification techniques, which includes machine learning. My goal is to minimize the burden on manual expert QC improving the consistency, performance, and reliability of the QC procedure for oceanographic data, especially for real-time operations.

CoTeDe is the result from several generations of quality control systems that started in 2006 with real-time QC of TSGs and were later expanded for other platforms including CTDs, XBTs, gliders, and others.


--------------
Why use CoTeDe
--------------

CoTeDe contains several QC procedures that can be easily combined in different ways:

- Pre-set standard tests according to the recommendations by GTSPP, EGOOS, XBT, Argo or QARTOD;
- Custom set of tests, including user defined thresholds;
- Two different fuzzy logic approaches: as proposed by Timms et. al 2011 & Morello et. al. 2014, and using usual defuzification by the bisector;
- A novel approach based on Anomaly Detection, described by `Castelao 2015 <http://arxiv.org/abs/1503.02714>`_.

Each measuring platform is a different realm with its own procedures, metadata, and meaningful visualization. 
So CoTeDe focuses on providing a robust framework with the procedures and lets each application, and the user, to decide how to drive the QC.
For instance, the `pySeabird package <http://seabird.castelao.net>`_ is another package that understands CTD and uses CoTeDe as a plugin to QC.


-------------
Documentation
-------------

A detailed documentation is available at http://cotede.readthedocs.org, while a collection of notebooks with examples is available at
http://nbviewer.ipython.org/github/castelao/CoTeDe/tree/master/docs/notebooks/
