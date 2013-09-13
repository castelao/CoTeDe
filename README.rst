=============
CoTe De l'eau
=============

This package is intended to quality control CTD stations by applying
a sequence of tests. It uses the PyCNV package to interpret the
SeaBird's .cnv output file.

This the result from several generations of quality control systems,
which started in 2006, while I was in charge of the quality control
of termosalinographs at AOML-NOAA, USA. Later I was advising the
quality control of the brazilian hydrography of PIRATA.

The tests implemented so far are just the traidional ones. When I
have a chance, I'll implement a new generation system that I've been
thinking about.

Quick howto
___________

First you need to have the CTD data:

    from seabird import cnv
    data = cnv.fCNV('example2.cnv')

Load it and run on the data:

    import cotede.qc
    ped = cotede.qc.ProfileQCed(data)

ped.keys will give you the data loaded from the CTD, simillar to the output from the fCNV

    ped.keys()

The Q.C. flags are at ped.flags

    ped.flags.keys()

For example, the Q.C. flags for temperature are at

    ped.flags['temperature'].keys()

Support and Documentation
-------------------------

How I see quality control
-------------------------

Quality control is different then data processing. On the processed data, the quality control/quality assurance means to check what looks fine. It is very important that the data is properly sampled, the quality control procedures can't go back on time and fix improper sampling, but only tell you that the data don't looks fine.

Why CoTeDe?
-----------

The full name of this package is CoTe De l'eau, which I understand
in my poor french to the something near to "rating the water". The
short name is cotede, to make easier for the users to remember,
since it is the quality control of COnductivity TEmperature and
DEpth (cotede).

