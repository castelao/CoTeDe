
Command line (ctdqc)
====================

A CTD data file can be quality controled from the shell script using the command line ctdqc. 
On this way it's easy to run the quality control from the shell, for example in a cron script for operational procedures.

In the shell one can run::

    $ ctdqc MyData.cnv

A new file is created, MyData_qced.nc with depth, temperature and salinity, with the respective quality control flags. 
It's used the default cotede setup of tests.

With the command line it's easy to run in a full collection of cnv files, like::

    for file in `find ./my_data_directory -iname '*.cnv'`;
    do ctdqc $file;
    done

This shell script will search for all .cnv files inside the directory ./my_data_directory (and sub-directories), evaluate each file and create on the side of the original data a netCDF with the QC flags.

In the future I'll turn this ctdqc command much more flexible.
