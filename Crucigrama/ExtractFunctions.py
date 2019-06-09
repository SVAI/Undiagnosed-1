# extract gene names
# python ExtractFunctions.py -f vep.deleterious.vep.txt -o vep.functions.tsv -goa goa_human.gaf -go go.obo -hpoa ALL_SOURCES_ALL_FREQUENCIES_genes_to_phenotype.txt -fun hp.obo
import argparse

def getGoa(goaFile):
    dict = {}
    with open(goaFile, 'r') as input:
        for row in input:
            if not row.startswith('!'):
                cols = row.strip('\n').split('\t')
                if cols[2] in dict:
                    dict[cols[2]].append(cols[4])
                else:
                    dict[cols[2]] = [cols[4]]
                #print('goa', cols[2], cols[4])
    return dict

def getGo(goFile):
    dict = {}
    with open(goFile, 'r') as input:
        for row in input:
            if row.startswith('[Term]'):
                idName = None
            else:
                if row.startswith('id: GO:'):
                    idName = 'GO:' + row.strip('\n').split(': GO:')[1]
                else:
                    if row.startswith('def:') and idName != None:
                        dict[idName] = row.strip('\n').split(':')[1].lstrip(' ').lstrip('"').rstrip('" [GOC')
                        #print('go', idName, dict[idName])
                        idName = None
    return dict

def getHpoa(hpoaFile):
    dict = {}
    with open(hpoaFile, 'r') as input:
        for row in input:
            if not row.startswith('#'):
                cols = row.strip('\n').split('\t')
                if cols[1] in dict:
                    dict[cols[1]].append(cols[3])
                else:
                    dict[cols[1]] = [cols[3]]
                #print('hpoa', cols[1], cols[3])
    return dict

def getHpo(hpoFile):
    dict = {}
    with open(hpoFile, 'r') as input:
        for row in input:
            if row.startswith('[Term]'):
                idName = None
            else:
                if row.startswith('id: HP:'):
                    idName = 'HP:' + row.strip('\n').split(': HP:')[1]
                else:
                    if row.startswith('def:') and idName != None:
                        dict[idName] = row.strip('\n').split(':')[1].lstrip(' ').lstrip('"').rstrip('" [HPO')
                        #print('go', idName, dict[idName])
                        idName = None
    return dict

def writeOutput(dictGenes, dictGenesFreq, outputFileName):
    output = open(outputFileName, 'w')
    for gene in dictGenes:
        output.write(gene + '\t' + str(dictGenesFreq[gene]) + '\t' + dictGenes[gene] + '\n')
    output.close()

def getGenesDesc(vepFileName, dictGoa, dictGo, dictHpoa, dictHpo, outputFileName):
    dictGenes = {}
    dictGenesFreq = {}
    countNotGoa = 0
    countGoa = 0
    countNotGo = 0
    countGo = 0
    with open(vepFileName, 'r') as input:
        for row in input:
            cols = row.strip('\n').split('\t')
            extraCol = cols[13].split(';')
            for eCol in extraCol:
                if eCol.startswith('SYMBOL='):
                    gene = eCol.split('=')
                    if gene[1] in dictHpoa:
                        if gene[1] in dictGenesFreq:
                            dictGenesFreq[gene[1]] += 1
                        else:
                            for goId in dictHpoa[gene[1]]:
                                if goId in dictHpo:
                                    dictGenes[gene[1]] = dictHpo[goId]
                                    dictGenesFreq[gene[1]] = 1
                                    countGo += 1
                                else:
                                    countNotGo += 1
                        countGoa += 1
                        #print('gene', gene[1], dictGenes[gene[1]])
                    else:
                        countNotGoa += 1
        print('count goa/not goa/go:', countGoa, countNotGoa)
        print('count go/not go:', countGo, countNotGo)
        print('genes found:', len(dictGenes))
    return dictGenes, dictGenesFreq

def main(vepFileName, goaFile, goFile, hpoaFile, hpoFile, outputFileName):
    dictGoa = getGoa(goaFile)
    dictGo  = getGo(goFile)
    dictHpoa = getHpoa(hpoaFile)
    dictHpo = getHpo(hpoFile)
    print('dict goa/go/hpoa/hpo:', len(dictGoa), len(dictGo), len(dictHpoa), len(dictHpo))
    dictGenes, dictGenesFreq = getGenesDesc(vepFileName, dictGoa, dictGo, dictHpoa, dictHpo, outputFileName)
    writeOutput(dictGenes, dictGenesFreq, outputFileName)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', help='vep file (vep.deleterious.vep.txt)')
    parser.add_argument('-goa', help='go annotation file (goa_human.gaf)')
    parser.add_argument('-go', help='go obo file (go.obo)')
    parser.add_argument('-hpoa', help='hpo annotation file (ALL_SOURCES_ALL_FREQUENCIES_genes_to_phenotype.txt)')
    parser.add_argument('-fun', help='human phenotype obo file (hp.obo)')
    parser.add_argument('-o', help='output file')
    args = parser.parse_args()
    main(args.f, args.goa, args.go, args.hpoa, args.fun, args.o)
