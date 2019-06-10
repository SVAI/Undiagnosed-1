library(dplyr)

#GUT eQTL
# >> /root/annot/db_to_bed/chr1_snps.gut.eQTL.txt

# OPEN CHROMATIN
# >> chr1_snps.gut.openchrom.txt


#CLINVAR
clinvar <- read.csv("/root/annot/db_to_bed/clinvar.temp", sep="\t", header=TRUE)
#clinvar <- read.csv("/root/annot/db_to_bed/clinvar.temp", sep="\t", header=TRUE)
colnames(clinvar)[1] <- "gene.symbol"
colnames(clinvar)[3] <- "rsID"
#filter out -1 values
clinvar <- clinvar %>%
filter(rsID !='-1')
#add "rs" to rsID
clinvar$rsID <- paste("rs", clinvar$rsID, sep="")  
# order by rsID numerically
clinvar <- clinvar[order(clinvar$rsID),]

#GWAShits
#GWAShits <- read.csv("/root/annot/db_to_bed/GWAShits.tmp", sep="\t", header=TRUE,nrows=1000)
GWAShits <- read.csv("/root/annot/db_to_bed/GWAShits.tmp", sep="\t", header=TRUE)
#GWAShits <- GWAShits[2:4]
GWAShits <- GWAShits[order(GWAShits$rsID),]

#merge by 
db.join <- merge(clinvar, GWAShits, by=c("rsID", "gene.symbol"), all=T)#[c("rsID", "gene.symbol", "pvalue")]
#db.join <- merge(clinvar, GWAShits, by=c("rsID", "gene.symbol"), all=T)
#print("clinvar")
#colnames(clinvar)
#print("GWAShits")
#colnames(GWAShits)
#db.join[1:5,]
nrow(clinvar)
nrow(GWAShits)
nrow(db.join)

# MERGE INTERSECTED VCF WITH DATABASE
vcf.intersection <- read.csv("/root/annot/vcf_intersection.bed", sep="\t", header=FALSE)
vcf.intersection <- vcf.intersection[c("V1", "V2", "V3", "V15")]
#head(vcf.intersection)
#colnames(vcf.intersection)
#rename V15

colnames(vcf.intersection) <- c("chr","start", "end", "rsID")

head(vcf.intersection)
cat("* Merge dbjoin and vcf intersection\n")
final.table <- merge(db.join, vcf.intersection, by=c("rsID"),all.y=TRUE)
head(final.table)

opchrom <- "/root/annot/db_to_bed/chr1_snps.gut.openchrom.txt"
epi <- "/root/annot/db_to_bed/chr1_snps.gut.eQTL.txt"

op <- read.delim(opchrom, sep="\t",h=F,as.is=T)
colnames(op)[1:3] <- c("chr","start","end")
colnames(op)[7:10] <- c("epi_chr","epi_start","epi_end","epi_state")
op <- op[,c(1:3,7:10)]
cat("* Merge finaltable with open chromatin\n")
x <- merge(x=final.table,y=op,by=c("chr","end"),all.x=TRUE)

epi <- read.delim(epi,sep="\t",h=F,as.is=T):
colnames(epi)[1:3] <- c("chr","start","end")
colnames(epi)[7] <- "eQTL_gut_gene"
x2 <- merge(x=x,y=epi,by=c("chr","end"),all.x=TRUE)
