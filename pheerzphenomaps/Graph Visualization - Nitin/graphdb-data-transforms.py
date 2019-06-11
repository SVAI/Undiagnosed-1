#!/usr/bin/env python
# coding: utf-8

# # John's Gene Analysis

# In this notebook, we load the manually (or using a software like Qiagen) curated list of genes of John, and visualize their relationships with Phenotypes, Metabolic Pathways and Variants as an interactive graph for John or his doctor or a researcher of his case. This visualization brings all information to a single place keeping their relationships intact backed by a powerful query engine.
# 
# This is developed as part of [SVAI Undiagnosed-1 Hackathon](https://sv.ai/undiagnosed-1-event) by [Team Pheerz Phenomaps](https://docs.google.com/presentation/d/1ZXT5jUo6xXdOTiBgAHEMkdiA7NQvlT2sAEywak2mAVI/edit#slide=id.gc6f80d1ff_0_50) in June 2019

# ## Introduction

# The big idea is to connect John's curated gene data with Phenotypes, Variants and Metabolic Pathways datasets as a big graph / network. And then visualize this massive data in an interactive manner on an easy to use user interface. For this we make use an open source graph database, [Neo4j](https://neo4j.com/developer/graph-database/), and host on a volatile remote storage, so that it is accessible by multiple researchers at once and yet gives us the control to completely bring it down whenever necessary.

# ## Setup

# - Launch a remote Neo4j server at https://neo4j.com/sandbox-v2/. A "Blank Sandbox" server is perfect for our use case. This is a volatile version of data store hosted by Neo4j Inc. for free for a couple of days. After that, it is taken down and the data is completely deleted. This is perfect for a hackthon on when playing around with data. However the same code can connect to any remote or local database server
# 
# - Install these Python dependencies

# In[ ]:


get_ipython().run_cell_magic('bash', '', '\npip install -q pandas requests py2neo')


# Wait for the Neo4j Sandbox to start. Then find these details in **Details** tab to make a secure connection to the remote database. For example, for the below sandbox
# 
# <img src="https://drive.google.com/uc?export=view&id=119NjH2koCTGuq7_N6eUucYrU8T3CgY3u" alt="example neo4j sandbox snapshot" />
# 
# the `BOLT_URL` is `bolt://34.203.33.130:36774`. Find yours and update in the next cell

# In[86]:


BOLT_URL = "bolt://34.203.33.130:36774"
USER = "neo4j"
PASSWORD = "fur-rollout-tempers" # better to read from an environment variable

from py2neo import Graph
graph = Graph( BOLT_URL, auth=(USER, PASSWORD) )
graph.run("match (n) return count(n)")
print("Connection successful!")


# In the **Get Started** tab above, click "Launch Browser" button to write interactive [graph queries](https://neo4j.com/docs/cypher-manual/3.5/introduction/). But before that we have to push John's data to that sandbox.
# 
# Email nithanaroy@gmail.com for John's data that is in a form, expected by this notebook.
# 
# Create a directory structure like below and save all of John's data in `./data/input` folder
# 
# ```
# ./data
# ├── input
# └── output
# ```

# ## Import Genes

# Import the curated list of genes from a CSV that has at least one column with list of Genes of interest
# 
# <table>
#     <thead>
#         <tr><th>Gene Symbol</th></tr>
#     </thead>
#     <tbody>
#         <tr><td>Gene1</td>
#         <tr><td>Gene2; Gene3</td>
#         <tr><td>Gene4; Gene2</td>
#     </tbody>
# </table>
# 
# As you can see some rows can have multiple of them separated by `;` And also the gene names can repeat

# In[7]:


import pandas as pd
from itertools import chain


# In[20]:


gene_names_raw = pd.read_csv("./data/input/curated-genes.csv")


# In[21]:


gene_names_raw.head()


# In[22]:


genes_df = gene_names_raw.apply( lambda g: g["Gene Symbol"].split(";"), axis=1 )


# In[23]:


genes_raw = list(chain.from_iterable( genes_df.tolist() ))


# In[31]:


genes = set( map( lambda g: g.strip(), genes_raw ) )


# In[32]:


len( list(genes) )


# Save results to disk

# In[33]:


pd.DataFrame(genes, columns=["gene"]).to_csv("./data/output/genes_list.csv", index=False)


# ## Fetch Phenotypes

# From http://uswest.ensembl.org we fetch the latest Phenotype information for each gene
# 
# 1. REST API documentation for fetching phenotypes http://rest.ensembl.org/documentation/info/phenotype_gene
# 2. http://uswest.ensembl.org/Homo_sapiens/Gene/Phenotype?db=core;g=ENSG00000139618;r=13:32315474-32400266 details of a sample Gene

# In[34]:


import requests
from time import sleep
from json import dump
import pandas as pd


# In[37]:


genes = pd.read_csv("./data/output/genes_list.csv")["gene"].to_list()


# In[39]:


len(genes)


# In[40]:


url = "http://rest.ensembl.org/phenotype/gene/homo_sapiens/{gene}"


# In[41]:


phenotypes_per_gene = {}


# In[66]:


get_ipython().run_cell_magic('time', '', '\nunknown_genes = []\nfailed_requests = []\nfor i, g in enumerate(genes):\n    r = requests.get( url.format(gene=g), headers={\'Content-type\': \'application/json\'} )\n    try:\n        resp = r.json()\n        if type(resp) == dict and "error" in resp:\n            unknown_genes.append(g)\n            continue\n\n        phenotypes_raw = map( lambda phenotype: phenotype.get("description", ""), r.json() )\n        phenotypes = filter( lambda phenotype: len(phenotype) > 1, phenotypes_raw )\n        phenotypes_per_gene[g] = list( phenotypes )\n    except ValueError:\n        failed_requests.append(g)\n    \n    sleep(0.05) # be kind to the API :P\n    if i % 100 == 0:\n        print( "Fetched {} genes\' info".format(i) )')


# In[67]:


print( "Phenotypes for %s genes are not found" % len(unknown_genes) )
print( "Due to network issues %s genes information couldn't be fetched" % len(failed_requests) )


# Number of genes for which at least 1 phenotype is found

# In[56]:


len( list(filter(lambda v: len(list(v)) > 0, phenotypes_per_gene.values() )) )


# Save results to disk

# In[69]:


with open("./data/output/gene_phenotypes_map.json", "w") as fp:
    dump(phenotypes_per_gene, fp)


# ### Push Gene-Phenotypes to Neo4J

# In[70]:


from json import load


# In[71]:


# load phenotype & genes map
with open("./data/output/gene_phenotypes_map.json", "r") as fp:
    phenotypes_per_gene = load(fp)


# In[89]:


get_ipython().run_cell_magic('time', '', '\nfor i, gene in enumerate(phenotypes_per_gene):\n    phenotypes = phenotypes_per_gene[gene]\n    for phenotype in phenotypes:\n        create_query = """\n            MERGE (g:Gene {name: "%(gene_name)s"})\n            MERGE (p:Phenotype {name: "%(phenotype_name)s"})\n            MERGE (g)-[r:causes]->(p)\n            RETURN g, r, p\n        """ % {"gene_name": gene, "phenotype_name": phenotype}\n        graph.run(create_query)\n        \n    if i % 10 == 0:\n        print( "Saved {} genes to Graph DB".format(i+1) )\n        \n# create index on name for faster insert queries later\ngraph.run( "CREATE INDEX ON :Gene(name)" ) ')


# In[90]:


len(phenotypes_per_gene.keys())


# ### Analyze

# In[104]:


graph.run("""
    MATCH (n:Gene)
    RETURN COUNT(n) AS TotalGenes
""").to_table()


# In[105]:


graph.run("""
    MATCH (n:Phenotype)
    RETURN COUNT(n) AS TotalPhenotypes
""").to_table()


# List the topk genes based on number of phenotypes they are connected to

# In[107]:


graph.run("""
    MATCH (k)
    WITH k, size((k)-[:causes]->(:Phenotype)) as out_degree
    order by out_degree desc
    RETURN k.name as Gene, out_degree as NumPhenotypesConnectedTo
    limit 10;
""").to_table()


# List the topk phenotypes based on number genes it is connected to

# In[111]:


graph.run("""
    match (p:Phenotype)
    with p, size((p)<--(:Gene)) as in_degree
    order by in_degree desc
    return p.name as Phenotype, in_degree as NumGenesConnectedTo
    limit 10
""").to_table()


# Use [Betweeness Centrality](https://neo4j.com/docs/graph-algorithms/current/algorithms/betweenness-centrality/) graph algorithm to identify topk influential Genes and Phenotypes

# In[121]:


graph.run("""
    CALL algo.betweenness.stream(null, "causes", {direction:'both'})
    YIELD nodeId, centrality
    MATCH (g) WHERE id(g) = nodeId
    RETURN g.name AS Gene__Phenotype, centrality
    ORDER BY centrality DESC
    LIMIT 15
""").to_table()


# ## Metabolic Pathways

# Link Genes to Metabolic Pathways

# In[91]:


from json import dump


# In[92]:


pathways_per_gene = {}


# Expected format of the mapping `.txt` file is
# 
# ```
# PathID1	Gene1	Gene2	Gene3	Gene4	Gene5
# PathID2	Gene6	Gene3
# ```
# 
# - Each row has details about a path
# - First value in each row is the path id / name
# - Subsequent fields are all genes
# - Each field in a row in separated by tabs

# In[94]:


with open("./data/input/keggGeneMapping.txt", "r") as fp:
    for l in fp:
        records = list( filter( lambda y: len(y) > 0, map( lambda x: x.strip(), l.strip().split("\t") ) ) )
        gene = records[0]
        pathways = records[1:]
        pathways_per_gene[gene] = pathways


# Save the pathways as JSON to disk

# In[95]:


with open("./data/output/pathways_per_gene.json", "w") as fp:
    dump(pathways_per_gene, fp)


# ### Push Pathways to Neo4J

# In[96]:


from json import load
import os


# In[98]:


# load phenotype & genes map
with open("./data/output/pathways_per_gene.json", "r") as fp:
    pathways_per_gene = load(fp)


# In[99]:


PATHWAY_IMAGES_FOLDER = "./data/input/pathview_images_full/"


# In[100]:


get_ipython().run_cell_magic('time', '', '\nmissing_pathway_files = []\n\npathway_png_template = "hsa%(pathway)s.pathview.png"\nfor i, pathway in enumerate(pathways_per_gene):\n    pathway_png = os.path.join( PATHWAY_IMAGES_FOLDER, pathway_png_template % {"pathway": pathway} )\n    if not os.path.exists(pathway_png):\n        pathway_png = "Yet to generate a pathway for me"\n        missing_pathway_files.append(pathway)\n    \n    genes = pathways_per_gene[pathway]\n    for gene in genes:\n        create_query = """\n            MERGE (g:Gene {name: "%(gene_name)s"})\n            MERGE (p:Pathway {name: "%(pathway)s", pathway_png: "%(pathway_png)s"})\n            MERGE (g)-[r:is_in]->(p)\n            RETURN g, r, p\n        """ % {"gene_name": gene, "pathway": pathway, "pathway_png": pathway_png}\n        graph.run(create_query)\n        \n    if i % 100 == 0:\n        print( "Saved {} pathways to Graph DB".format(i) )')


# In[53]:


len(pathways_per_gene.keys())


# ### Analyze

# In[122]:


graph.run("""
    MATCH (n:Pathway)
    RETURN COUNT(n) AS TotalPathways
""").to_table()


# ## Variants & Genes

# In[125]:


import pandas as pd


# The variants CSV file is expected to have these columns,
# 
# <table>
#     <thead>
#         <tr>
#             <th>gene</th>
#             <th>Position</th>
#             <th>Variation Type</th>
#             <th>Gene Region</th>
#             <th>dbSNP ID</th>
#             <th>1000 Genomes Frequency</th>
#         </tr>
#     </thead>
#     <tbody>
#         <tr>
#             <td>Gene1</td>
#             <td>1234</td>
#             <td>Insertion</td>
#             <td>Intronic</td>
#             <td>4321</td>
#             <td>&nbsp</td>
#         </tr>
#         <tr>
#             <td>..</td>
#             <td>...</td>
#             <td>...</td>
#             <td>...</td>
#             <td>...</td>
#             <td>...</td>
#         </tr>
# </table>

# In[123]:


v_df = pd.read_csv("./data/input/variants.csv")


# In[124]:


v_df.shape


# In[130]:


v_df.head()


# In[131]:


df = v_df.fillna({ 
    "1000 Genomes Frequency": 0
})


# In[132]:


df.head()


# In[129]:


df.describe()


# ### Push Variants to Neo4J

# As there 120K+ variants saving all of them to Neo4j, at least the way below, can take a while. So pick how many rows from the above dataframe you want to push. Email nithanaroy@gmail.com if this is really crucial for your analysis and should be optimized to run faster.

# In[136]:


max_rows_to_push = 130000


# In[135]:


get_ipython().run_cell_magic('time', '', '\nfor i, r in df.iterrows():\n    create_query = """\n                MERGE (g:Gene {name: "%(gene_name)s"})\n                MERGE (p:Variant {name: "%(variant)s", gene_region: "%(gene_region)s", freq_1000: %(freq_1000)s})\n                CREATE (g)-[r:has {variant_type: "%(variant_type)s", position: %(position)s}]->(p)\n                RETURN g, r, p\n            """ % {\n        "gene_name": r["gene"],\n        "variant": r["dbSNP ID"],\n        "gene_region": r["Gene Region"],\n        "freq_1000": r["1000 Genomes Frequency"],\n        "variant_type": r["Variation Type"],\n        "position": r["Position"]\n    }\n    graph.run(create_query)\n\n    if i % 10000 == 0:\n        print("Saved {} variants".format(i))')


# Intentionally interrupted the push after 6 hours as this is only a hackathon demo with real data! But this can be continued for real analysis

# ### Analyse

# In[141]:


graph.run("""
    MATCH (v:Variant)
    RETURN COUNT(v) as TotalVariants
""").to_table()


# As we interrupted the transaction, it may lead to inconsistent data. Let's find out how many Variants have proper names

# In[143]:


graph.run("""
    match (p:Variant)
    where p.name <> "nan"
    return count(p) as Count
""").to_table()


# List the topk genes based on number of variants it is has

# In[138]:


graph.run("""
    MATCH (k)
    WITH k, size((k:Gene)-[:has]->(:Variant)) as out_degree
    order by out_degree desc
    RETURN k.name as Gene, out_degree as NumVariants
    limit 10;
""").to_table()


# List the topk variants based on number genes it can originate from

# In[139]:


graph.run("""
    match (p:Variant)
    with p, size((p)<--(:Gene)) as in_degree
    order by in_degree desc
    return p.name as Variant, in_degree as NumGenesConnectedTo
    limit 10
""").to_table()


# Unfortunately the top variants were corrupted due to interrupting the push to Neo4j. This should'nt happen if you are not impatient like me ;)

# In[144]:


graph.run("""
    match (p:Variant)
    where p.name <> "nan"
    with p, size((p)<--(:Gene)) as in_degree
    order by in_degree desc
    return p.name as Variant, in_degree as NumGenesConnectedTo
    limit 10
""").to_table()


# Topk variants with high variation when compared with 1000 Genomes

# In[151]:


graph.run("""
    match (v:Variant)
    return v.name as High_1000Genome_Freq, v.freq_1000 as Frequency
    order by Frequency DESC
    limit 10
""").to_table()


# ## Interactive Visualization

# One of the biggest strengths of Neo4j besides scaling is its in-built visualization tool. The tool can be launched by pushing "Launch Browser" button in the "Details" page on Sandbox page.
# 
# Once the browser is open, besides all the above queries, queries which return not just tables of information, but sub-graphs from entire graphs can be visualized in an interactive manner.
# 
# Checkout the screen recording to get a glimpse of what's possible

# <img src="https://drive.google.com/uc?export=view&id=1Q95tj5VmKLdA1uqW_pQbFJgeUKE2x6zt" alt="example neo4j sandbox snapshot" />

# That's all folks! Let's hope this helps solve John's case :)
