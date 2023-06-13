======
CoTeDe
======

.. image:: https://joss.theoj.org/papers/10.21105/joss.02063/status.svg
   :target: https://doi.org/10.21105/joss.02063

.. image:: https://zenodo.org/badge/10284681.svg
   :target: https://zenodo.org/badge/latestdoi/10284681

.. image:: https://readthedocs.org/projects/cotede/badge/?version=latest
   :target: https://cotede.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://github.com/castelao/CoTeDe/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/castelao/CoTeDe/actions/workflows/ci.yml)

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


----------
Why CoTeDe
----------

CoTeDe contains several QC procedures that can be easily combined in different ways:

- Pre-set standard tests according to the recommendations by GTSPP, EGOOS, XBT, Argo or QARTOD;
- Custom set of tests, including user defined thresholds;
- Two different fuzzy logic approaches: as proposed by Timms et. al 2011 & Morello et. al. 2014, and using usual defuzification by the bisector;
- A novel approach based on Anomaly Detection, described by `Castelao 2021 <https://doi.org/10.1016/j.cageo.2021.104803>`_ (available since 2014 `<http://arxiv.org/abs/1503.02714>`_).

Each measuring platform is a different realm with its own procedures, metadata, and meaningful visualization. 
So CoTeDe focuses on providing a robust framework with the procedures and lets each application, and the user, to decide how to drive the QC.
For instance, the `pySeabird package <http://seabird.castelao.net>`_ is another package that understands CTD and uses CoTeDe as a plugin to QC.

-------------
Documentation
-------------

A detailed documentation is available at http://cotede.readthedocs.org, while a collection of notebooks with examples is available at
http://nbviewer.ipython.org/github/castelao/CoTeDe/tree/master/docs/notebooks/

--------
Citation
--------

If you use CoTeDe, or replicate part of it, in your work/package, please consider including the reference:

Castelão, G. P., (2020). A Framework to Quality Control Oceanographic Data. Journal of Open Source Software, 5(48), 2063, https://doi.org/10.21105/joss.02063

::

  @article{Castelao2020,
    doi = {10.21105/joss.02063},
    url = {https://doi.org/10.21105/joss.02063},
    year = {2020},
    publisher = {The Open Journal},
    volume = {5},
    number = {48},
    pages = {2063},
    author = {Guilherme P. Castelao},
    title = {A Framework to Quality Control Oceanographic Data},
    journal = {Journal of Open Source Software}
  }

For the Anomaly Detection techinique specifically, which was implemented in CoTeDe, please include the reference:

Castelão, G. P. (2021). A Machine Learning Approach to Quality Control Oceanographic Data. Computers & Geosciences, https://doi.org/10.1016/j.cageo.2021.104803

::

  @article{Castelao2021,
    doi = {10.1016/j.cageo.2021.104803},
    url = {https://doi.org/10.1016/j.cageo.2021.104803},
    year = {2021},
    publisher = {Elsevier},
    author = {Guilherme P. Castelao},
    title = {A Machine Learning Approach to Quality Control Oceanographic Data},
    journal = {Computers and Geosciences}
  }

If you are concerned about reproducibility, please include the DOI provided by Zenodo on the top of this page, which is associated with a specific release (version).
