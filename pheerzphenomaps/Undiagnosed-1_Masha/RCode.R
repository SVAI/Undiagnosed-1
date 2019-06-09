library(pathview)
MyData <- read.csv(file="/Users/Masha/Documents/Projects/Undiagnosed-1/keggGeneMapping.txt", header=FALSE, sep="\t")

for(row in 1:nrow(MyData)){
  # print(MyData[row,])
  pathwayNum = MyData[row,1]
  print("num:")
  if (pathwayNum == "01100"){
    next
  }
  print(pathwayNum)
  myStr = as.character("")
  for (col in 2:ncol(MyData)){
    print(MyData[row,col])
    if (is.na(MyData[row, col])){
      next
    }
    else if (MyData[row,col] == "" | MyData[row,col] == "NA"){
      next
    }
    geneName = (MyData[row,col])
    # print(geneName)
    myStr = paste(myStr, geneName)

    
  }
  myStr = unlist(strsplit(myStr, split=" "))
  myStr = myStr[2:length(myStr)]
  print(myStr)
  mapped_gene_data = id2eg(myStr, category = "SYMBOL", org = "hsa", pkg.name = NULL)
  
  download.kegg(pathway.id = pathwayNum, species = "hsa", kegg.dir = ".",
                file.type=c("xml", "png"))
  print("generating pathview")
  pathview(gene.data = mapped_gene_data[,2], pathway.id = pathwayNum,
         species = "hsa", kegg.dir = ".", gene.annotpkg = NULL, min.nnodes = 3, kegg.native = TRUE,
         map.null = TRUE, expand.node = FALSE, split.group = FALSE, map.symbol =
           TRUE, map.cpdname = TRUE, node.sum = "sum", discrete=list(gene=TRUE,
                                                                     cpd=FALSE), limit = list(gene = 1, cpd = 1), bins = list(gene = 10, cpd
                                                                                                                              = 10), both.dirs = list(gene = T, cpd = T), trans.fun = list(gene =
                                                                                                                                                                                             NULL, cpd = NULL), low = list(gene = "red", cpd = "blue"), mid =
           list(gene = "red", cpd = "gray"), high = list(gene = "red", cpd =
                                                            "yellow"), na.col = "transparent")
  print("pathview generated")
}

