# BroLogSplit
Will split large bro log files into smaller log files by date. 

Purpose: Split bro logs into gzip files by date.

Usage:

    $ ./split_brolog.py <filename> [<YYYYMMDD>]
    filename    The bro log to split. Can be regular, gz, or xz file.
    YYYYMMDD    OPTIONAL timestamp. Tells script what day to start creating output files from.
