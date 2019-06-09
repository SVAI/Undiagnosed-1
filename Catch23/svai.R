## Got chrommosome positions from immune genes
immport = read.csv("Geneappend3.csv", stringsAsFactors = F)

library("biomaRt")
ensembl=useMart("ensembl", host="grch37.ensembl.org",dataset="hsapiens_gene_ensembl")
out=getBM(mart = ensembl, attributes = c("external_gene_name","chromosome_name","start_position","end_position"), filters = "external_gene_name", values = unique(immport$Symbol))
out$immportchr=unlist(lapply(out$external_gene_name, function(x) {y=immport[immport$Symbol == x,]; return(unique(y$Chromosome))}))
out$immportsymbol=unlist(lapply(out$external_gene_name, function(x) {y=immport[immport$Symbol == x,]; return(unique(y$Symbol))}))
out$pos=paste0(out$immportchr,":",out$start_position-500,"-",out$end_position+500)

write.table(out$pos, "immunoGenePositions.txt", sep="\t", row.names = FALSE, col.names = FALSE, quote=FALSE)


for (i in unique(immport$Symbol)) {
  a = getBM(mart=ensembl, attributes=c("external_gene_name","chromosome_name","start_position","end_position"), filters = "external_gene_name", values=i)
  if (nrow(a) > 1) {
    print(i)
  }
}


## Output of VEP for immune variants
vep = read.table('vep_immuno1.txt', stringsAsFactors = FALSE)
colnames(vep) = c('UploadedVariant','Location','Allele','Consequence','Impact','Symbol','Gene','FeatureType','Feature','Biotype','Exon','Intron','HGVSc','HGVSp','cDNAposition','CDSposition','ProteinPosition','AminoAcids','Codons','ExistingVariant','DistanceToTranscript','FeatureStrand','FLAGS','SymbolSource','HGNCID','TranscriptSupportLevel','APPRIS','SIFT','PolyPhen','AF','AFR_AF','AMR_AF','EAS_AF','EUR_AF','SAS_AF','ClinicalSignificance','SomaticStatus','Phenotype','Pubmed','MotifName','MotifPosition','HighInfoPosition','MotifScoreChange','MPC','LoFtool','Condel','CADD_PHRED','CADD_RAW')
vep$EUR_AF = as.numeric(vep$EUR_AF)
vep$CADD_PHRED = as.numeric(vep$CADD_PHRED)
vep_maf = vep[vep$EUR_AF <= 0.01,]
vep_maf = vep_maf[!is.na(vep_maf$EUR_AF),]
vep_maf = vep_maf[order(vep_maf$EUR_AF),]
maf_genes = unique(vep_maf$Symbol)
write.table(maf_genes, "vep_immuno1_maf_genes.txt", sep="\t", row.names=FALSE, col.names=FALSE, quote=FALSE)

vep_maf_cadd = vep_maf[vep_maf$CADD_PHRED >= 10,]
vep_maf_cadd = vep_maf_cadd[!is.na(vep_maf_cadd$CADD_PHRED),]
vep_maf_cadd = vep_maf_cadd[order(-vep_maf_cadd$CADD_PHRED),]
mafcadd_genes = unique(vep_maf_cadd$Symbol)
write.table(mafcadd_genes, "vep_immuno1_mafcadd_genes.txt", sep="\t", row.names=FALSE, col.names=FALSE, quote=FALSE)


## Structural variants
sv = read.table('exonicSVGenes.bed', fill=TRUE, sep='\t', stringsAsFactors = F)
colnames(sv) = sv[1,]
sv = sv[-1,]
sv_genes = sv$gene
all=c()
for (i in sv_genes) {
  s = gsub("\\[(.*)\\]","\\1",i)
  all=c(all,unlist(strsplit(s, ",")))
}
all=trimws(all)

sv_pos=paste0(gsub("chr(.*)","\\1",sv$chrom),":",as.numeric(sv$start)-500,"-",as.numeric(sv$end)+500)
write.table(sv_pos, "svGenePositions_500.txt", sep="\t", row.names = FALSE, col.names = FALSE, quote=FALSE)

sv_pos=paste0(gsub("chr(.*)","\\1",sv$chrom),":",as.numeric(sv$start),"-",as.numeric(sv$end))
write.table(sv_pos, "svGenePositions.txt", sep="\t", row.names = FALSE, col.names = FALSE, quote=FALSE)


## Intersect SV and immune
sv_immune_genes = intersect(unique(all), maf_genes)
sv_immune = vep_maf[vep_maf$Symbol %in% sv_immune_genes,]

