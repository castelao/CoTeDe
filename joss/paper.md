---
title: 'A Framework to Quality Control Oceanographic Data'
tags:
  - Python
  - oceanography
  - quality control
authors:
  - name: Guilherme P. Castelao
    orcid: 0000-0002-6765-0708
    affiliation: 1 # (Multiple affiliations must be quoted)
affiliations:
 - name: Scripps Institution of Oceanography
   index: 1
date: 11 November 2019
bibliography: paper.bib
---

# Summary

The ocean is an intrinsically challenging environment to collect data, which makes spurious measurements inevitable. Thus, the quality of oceanographic datasets is highly dependent on the ability to identify and remove bad samples. Quality control (QC) of oceanographic data has mostly relied on manual QC by experts, which, despite resulting in the best data quality, is not scalable and becomes impractical to handle large datasets or real-time data streams. To address this issue, automatic QC procedures have been proposed and widely used for decades [e.g., @IOC26; @GTSPP:2010; @EGOOS:2010; @Argo:2015; @QARTOD:2016; @Morello:2014]; however, these procedures are seldom organized and distributed as packages, so it is still common for new users to have to implement them from scratch. Additionally, different applications of the same dataset may require different QC procedures. For example, a particular user faced with the QC of a small dataset might be willing to apply a less conservative QC in order to preserve a larger number of data points, paying the price of having some false positives. CoTeDe is an Open Source Python package that provides a flexible way to automatic QC oceanographic data by combining multiple QC standards while allowing the users to fully control and tune the parameters according to their own needs.


Automatic QC traditionally consists of a sequence of tests that identify spurious measurements based on different criteria; thus, it is common to aggregate multiple tests to cover a more extensive possibility of problems. With that in mind, the tests of the most common QC procedures were implemented in CoTeDe in a modular fashion to facilitate expanding with new tests and to permit alternative arrangements. The user can choose from one of the built-in standard procedures, for example, the Argo recommendations [@Argo:2015], or compose a custom arrangement of tests. This freedom allows a better data assessment by fine-tuning the methods -- A Spray underwater glider operating on the California coast might benefit from slightly different thresholds than used to QC the same Spray in the Mediterranean. The custom QC procedures can be saved as JSON descriptors to be re-used or shared so that experts can develop a diverse collection of alternative procedures without necessarily requiring more coding. The implementation of such a versatile system was simplified by adopting a generic data model object that standardizes the data and metadata access, resulting in a platform-agnostic system that could equally evaluate data from an XBT or a Spray underwater glider with the appropriate tests. For instance, the concept of the World Ocean Atlas climatology comparison test [@GTSPP:2010] is the same for a profile from an XBT or a CTD, being only necessary to inform the observed temperature, geolocation, and time. Finally, CoTeDe dependencies were intentionally minimized to simplify its adoption by other packages.




Modern oceanography relies on an unprecedented abundance of measurements that keeps increasing every day [see @WOD2018]. In the past couple of decades, traditional observational systems have been complemented by autonomous platforms like Argo, Spray underwater gliders, and Saildrones, which can provide nearly continuous data streams. Thus, QC procedures for oceanographic data must evolve to keep pace with the ever-growing dataflow. In this context, CoTeDe was developed to reduce the burden on manual expert QC with automation, which enables experts to focus their effort on the most challenging cases. CoTeDe was designed to attend not only individual scientists but also real-time operations on large data centers while providing a flexible framework to implement novel QC approaches such as fuzzy logic and machine learning. This is the result of several generations of quality control systems, and some of the most notable applications of CoTeDe have been the QC of real-time thermosalinograph operations by the Atlantic Oceanographic and Meteorological Laboratory - NOAA (AOML) in 2006; PIRATA hydrographic cruises by the National Institute for Space Research (INPE) in 2011; and a novel approach to optimize expert manual QC by the International Quality Controlled Ocean Database (IQuOD), since 2015.


# Acknowledgements

The author acknowledges the support from the Sao Paulo Research Foundation (FAPESP) on grant 2013/11825-0, the national committees of the Scientific Committee on Oceanic Research (SCOR) - WG148 (IQuOD), and the International Oceanographic Data and Information Exchange program of the Intergovernmental Oceanographic Commission (IOC). Luiz Irber and Andrew Ng had great influence on improving CoTeDe. Thanks to Bia Villas Boas for the suggestions on this manuscript and the documentation.

# References
