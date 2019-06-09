# extract gene names
# python ExtractGenes.py -f vep.deleterious.vep.txt -o vep.genes.tsv -goa goa_human.gaf -go go.obo
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

def writeOutput(dictGenes, dictGenesFreq, outputFileName):
    output = open(outputFileName, 'w')
    for gene in dictGenes:
        output.write(gene + '\t' + str(dictGenesFreq[gene]) + '\t' + dictGenes[gene] + '\n')
    output.close()

def getGenesDesc(vepFileName, dictGoa, dictGo, outputFileName):
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
                    if gene[1] in dictGoa:
                        if gene[1] in dictGenesFreq:
                            dictGenesFreq[gene[1]] += 1
                        else:
                            for goId in dictGoa[gene[1]]:
                                if goId in dictGo:
                                    dictGenes[gene[1]] = dictGo[goId]
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

def main(vepFileName, goaFile, goFile, outputFileName):
    dictGoa = getGoa(goaFile)
    dictGo  = getGo(goFile)
    print('dict goa/go:', len(dictGoa), len(dictGo))
    dictGenes, dictGenesFreq = getGenesDesc(vepFileName, dictGoa, dictGo, outputFileName)
    writeOutput(dictGenes, dictGenesFreq, outputFileName)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', help='vep file')
    parser.add_argument('-goa', help='go annotation file')
    parser.add_argument('-go', help='go obo file')
    parser.add_argument('-o', help='output file')
    args = parser.parse_args()
    main(args.f, args.goa, args.go, args.o)
