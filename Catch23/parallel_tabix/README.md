## overview

this bash program takes as input a file name, with a list of CHR:START-STOP records (one per line) and runs `tabix` on a hard-coded compressed vcf file, generating a tabix outfile file for each record. the program runs N instances of tabix in parallel, as defined by a parameter.

## usage

```
$ ./par_tabix.sh <filename> <number>

```
where, string is the file name of the input file with a list of CHR:START-STOP records
and <number> is the parallelism, i.e. number of tabix instances running in parallel.
