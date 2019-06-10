#!/bin/bash


clinvar_file=/root/annot/CLINVAR_variant_summary_chr1.txt

cat  $clinvar_file | awk -F "\t" '{print $5"\t"$7"\t"$10"\t"$14}' | uniq  > clinvar.temp
 

GWAShits=/root/software/Undiagnosed_tools/NHGRI_GWAS/GWAShits_EFO_0000589.txt.formatted.txt
awk -F "\t" '{print $1"\t"$3"\t"$13"\t"$15}' $GWAShits |uniq > GWAShits.tmp


