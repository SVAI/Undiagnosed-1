#!/bin/bash
f='svGenePositions_500.txt'
while read p; do
	echo "tabix -f /root/notebooks/patient-data/WGS/DeepVariant_VCFs/SQ9887_L00.reheader.vcf.gz $p" >> svOut_500.sh
done < $f

