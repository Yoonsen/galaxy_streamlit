import streamlit as st
import gnl as gnl
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image
import requests
import community
import streamlit as st
import streamlit.components.v1 as components
import json




# Convert graph data to JSON and then to bytes

#url = "http://35.228.68.102.nip.io/galaxies/query"
#url = "http://35.228.68.102/galaxies/query"
url = "https://api.nb.no/dhlab/nb_ngram_galaxies/galaxies/query"

colors =  ['#DC143C','#FFA500',
           '#F0E68C','#BC8F8F','#32CD32',
           '#D2691E','#3CB371','#00CED1',
           '#00BFFF','#8B008B','#FFC0CB',
           '#FF00FF','#FAEBD7']

def word_to_colors(comm):
    word_to_color = dict()
    for i, e in enumerate(comm.values()):
        for x in e:
            word_to_color[x] = colors[i % len(colors)]
    return word_to_color



@st.cache_data()
def word_graph(word = None, cutoff = 20, corpus = 'all'):
    """ corpus = bok, avis or all"""
    params = {
        'terms':word, 
        'leaves':0,
        'limit':cutoff,
        'corpus':corpus,
    }
    r = requests.get(url, params = params)
    G = nx.DiGraph()
    edgelist = []
    if r.status_code == 200:
        #graph = json.loads(result.text)
        graph = r.json()
        #print(graph)
        nodes = graph['nodes']
        edges = graph['links']
        for edge in edges:
            source, target = (nodes[edge['source']]['name'], nodes[edge['target']]['name'])
            if source.isalnum() and target.isalnum():
                edgelist += [(source, target, abs(edge['value']))]
        G.add_weighted_edges_from(edgelist)
    return G

@st.cache_data()
def path(graph = None, source = None, target = None):
    if nx.is_directed(graph):
        k = 'directed'
    else:
        k = 'undirected'
    try:
        res = (source, target, k, nx.shortest_path(graph, source = source, target = target))
    except:
        res = (source, target, 'nopath', [])
    return res

@st.cache_data()
def paths(graph = None, source = None, target = None, cutoff = 3):
    if nx.is_directed(graph):
        k = 'directed'
    else:
        k = 'undirected'
    try:
        res = (source, target, k, list(nx.all_simple_paths(graph, source = source, target = target, cutoff = cutoff)))
    except:
        res = (source, target, 'nopath', [])
    return res

@st.cache_data()
def galaxy(word, lang='nob', corpus = 'all', cutoff = 16):
    if lang == 'nob':
        res = word_graph(word, corpus = corpus, cutoff = cutoff)
    else:
        res = nb.make_graph(word, lang = lang, cutoff = cutoff)
   
    comm = gnl.community_dict(res)
    cliques = gnl.kcliques(res.to_undirected())
    return res, comm, cliques




def make_write_graphs(word, folder = None ,cutoff = 50, template = "graph_template_force.html",corpus='all'):
   
    G = word_graph(word, cutoff = cutoff, corpus=corpus)
    G.remove_edges_from(nx.selfloop_edges(G))
    partition = community.best_partition(G.to_undirected())
    centrality = nx.degree_centrality(G.to_undirected())

    data = {
        "nodes": [{"id": node, "centrality": centrality[node],  "community": partition[node]} for node in G.nodes()],
        "links": [{"source": u, "target": v} for u, v in G.edges()]
    }
    with open(template) as t:
        template_html = t.read()
    #print(template_html)
    html = (template_html
            .replace("NODES_FROM_DATA", json.dumps(data['nodes']))
            .replace("LINKS_FROM_DATA", json.dumps(data['links']))
           )
    
    return G, html


st.set_page_config(layout="wide")

head_col1,_,_,head_col2, head_col3 = st.columns(5)

with head_col1:
    st.title('Ordnettverk')
with head_col2:
    st.markdown("""Les mer om [DH ved Nasjonalbiblioteket](https://nb.no/dh-lab)""")
with head_col3:
    image = Image.open("DHlab_logo_web_en_black.png")
    st.image(image)

p_col1, p_col2, p_col3 = st.columns(3)
with p_col1:
    words = st.text_input('Skriv inn ett ord eller flere adskilt med komma', 'frihet', help=" Det skilles mellom store og små bokstaver")
    
with p_col2:
    corpus = st.selectbox('Bøker eller aviser', ['begge', 'bok', 'avis' ], help="Grafer basert på bare bøker eller bare aviser")
    if corpus == 'begge':
        corpus = 'all'

with p_col3:
    cutoff = st.number_input('Tilfang av noder', min_value = 12, max_value =24, value = 18, 
                                 help="Angi et tall mellom 12 og 24 - jo større, jo fler noder -"
                                 " effektiv kun for norsk 'nob'")


st.write("### Graf")

Graph, G_html = make_write_graphs(words, cutoff = cutoff, corpus = corpus)



components.html(G_html, height=800)




#------------------------------------------- Path ---------------------------------###############

