
Command line (ctdqc)
====================

A CTD data file can be quality controled from the shell script using the command line ctdqc. 
On this way it's easy to run the quality control from the shell, for example in a cron script for operational procedures.

In the shell one can run::

    $ ctdqc MyData.cnv

A new file is created, MyData_qced.nc with depth, temperature and salinity, with the respective quality control flags. 
It's used the default cotede setup of tests.

In the future I'll turn this script much more flexible.
