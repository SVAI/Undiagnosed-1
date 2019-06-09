Disclaimer: 
The content and results are not intended to be a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. Never disregard professional medical advice or delay in seeking it because of something you have read on this repository. 

Team Members:
* Rilson Nascimento, MS, Salesforce
* Usman Qazi, PhD, Artelus
* Lei Pan, MS, Databricks
* Jordan Wilheim
* Candace Liu, Stanford
* Andrew Sharo, Stanford

Our Approach
Find SNPs in WGS (DeepVariant) vcfs within gene coding regions and 500 bp away from gene coding.
Immune genes were filtered outDetermine MAF using [VEP](https://uswest.ensembl.org/info/docs/tools/vep/index.html)
Filter common variants in european populations (1% MAF) 
Run Results through [Enrichr](https://amp.pharm.mssm.edu/Enrichr/) for enrichment analysis. 
Find the intersection between SV and SNPs in order to detect possible double mutations. 
From this subset, determine functional significance of regions and associated variation. 


