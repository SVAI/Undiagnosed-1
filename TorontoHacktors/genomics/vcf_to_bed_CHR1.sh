#!/bin/bash
#vcfFile=/root/notebooks/patient-data/Exome/variants.vcf
vcfFile=/root/notebooks/patient-data/WGS/DeepVariant_VCFs/SQ9887_L00.reheader.vcf.gz
dbSNP=/root/annot/dbsnp151.bed
#mart_export=/root/annot/mart_export.txt
#mart_export_SNPs_bed=/root/annot/mart_export_SNPs.bed
outDir=/root/annot/outdir
mkdir -p $outDir

bedOut=vcf_called.bed
# CONVERT MART EXPORT TO BED
#cat $mart_export | grep -v '-' | awk 'BEGIN{OFS="\t";}{print $3,$4,$5,$1,$2,$6,$7 }' |  grep -v Variant > $mart_export_SNPs_bed

echo "* Convert called VCF file to bed"
#ONLY CHROMOSOME 1
zcat $vcfFile | grep -v \# | grep "^1\s" | awk 'BEGIN {OFS="\t";}{print "chr"$1,$2-1,$2,$3,$4,$5,$6,$7,$8,$9,$10}' > $bedOut
#bedtools intersect -wa -wb -a $bedOut -b $mart_export > vcf_intersection.bed 
echo "sort bed files"
bedOutSorted=vcf_called.sorted.bed
sort -k1,1 -k2,2n -k3,3n $bedOut > $bedOutSorted
dbSNPSorted=/root/annot/dbsnp151.sorted.bed
####sort -k1,1 -k2,2n -k3,3n $dbSNP > $dbSNPSorted
echo "bedtools intersect"
bedtools intersect -wa -wb -a $bedOutSorted -b $dbSNPSorted > vcf_intersection.bed 

#SCRAP
# bedSort
# http://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64/bedSort
#
# bedtools
# https://bedtools.readthedocs.io/en/latest/content/installation.html

#/root/output/variant2gene/chr22_snps.recode.vcf
#----------------
# Convert VCF into bed file for bedtools
#chrom=22
#pfxOut=${outDir}/chr${chrom}_snps
#cat ${pfxOut}.recode.vcf | grep -v "^#" | cut -f 1-5 | awk '{print "chr"$1"\t"$2"\t"$2"\t"$3"\t"$4"\t"$5}'>$bedOut
# ----------------
# intersect with bedtools
#bedtools intersect -wa -wb -a $bedOut -b $eqtlFile | cut -f1-4,9-11 | uniq >  ${pfxOut}.${setName}.eQTL.txt
