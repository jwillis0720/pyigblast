PyIgBlast
=========

PyIgBlast - Open source Parser to call IgBlast and parse results for high-throughput sequencing. 
Uses Python multi-processing to get around bottlenecks of IgBlast multi-threading. 
Parses blast output to deliminated files (csv,json) for uploading to databases. 
Can connect directly with mysql and mongo instances to insert directly.

Requires
=========

1.   [Biopython - Python tools for biological computations](http://biopython.org/wiki/Download)
2.   [Igblastn - BLAST algorithm for analyzing immunoglobulin repertoires](ftp://ftp.ncbi.nih.gov/blast/executables/igblast/release/)

8/6/2013 Full functionality with multiprocessing and a formatting template

8/7/2013 Can run on blue cluster

8/9/2013 Parses output from igblast into python classes
