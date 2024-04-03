import streamlit as st
import gnl as gnl
#import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image
import requests
import community
import streamlit as st
import streamlit.components.v1 as components
import json



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


def galaxy(word, lang='nob', corpus = 'all', cutoff = 16):
    if lang == 'nob':
        res = word_graph(word, corpus = corpus, cutoff = cutoff)
    else:
        res = nb.make_graph(word, lang = lang, cutoff = cutoff)
   
    comm = gnl.community_dict(res)
    cliques = gnl.kcliques(res.to_undirected())
    return res, comm, cliques


    
st.set_page_config(page_title="Nettverk", layout="wide")

head_col1, head_col2, head_col3 = st.columns([3,1,1])

with head_col1:
    st.title('Ordnettverk')
    st.markdown("""Les mer om [DH ved Nasjonalbiblioteket](https://nb.no/dh-lab)""")
with head_col2:
    pass
with head_col3:
    image = Image.open("DHlab_logo_web_en_black.png")
    st.image(image)

st.markdown("---")
    
p_col1, p_col2, p_col3 = st.columns([2,1,1])
with p_col1:
    words = st.text_input('Skriv inn ett ord eller flere adskilt med komma', 'frihet', help=" Det skilles mellom store og små bokstaver")
with p_col2:
    corpus = st.selectbox('Bøker eller aviser', ['begge', 'bok', 'avis' ], help="Grafer basert på bare bøker eller bare aviser")
    if corpus == 'begge':
        corpus = 'all'

with p_col3:
    cutoff = st.number_input('Tilfang av noder', min_value = 10, max_value =24, value = 12, help="Angi et tall mellom 12 og 24 - jo større, jo fler noder")


data_col1, data_col2, data_col3, data_col4 = st.tabs(["Graf", "Clustre", "Klikkstruktur", "Sti mellom noder"])

Graph, G_html = make_write_graphs(words, cutoff = cutoff, corpus = corpus)

#nodes, edges, config = create_nodes_and_edges_config(Graph, comm)


with data_col1:
    components.html(G_html, height=1000)
        

with data_col2:
    comm = gnl.community_dict(Graph)

    #------------------------------------------ Clustre -------------------------------###

    #st.write('### Clustre')
    st.write('\n\n'.join(['**{label}** {value}'.format(label = key, value = ', '.join(comm[key])) for key in comm]))


    #----------------------------------------- cent

with data_col3:
    #st.write('### Klikkstruktur')
    cliques = gnl.kcliques(Graph.to_undirected())

    st.write('\n\n'.join(["{a}: {b}".format(a = '-'.join([str(x) for x in key]), b = ', '.join(cliques[key])) for key in cliques]))


#------------------------------------------- Path ---------------------------------###############


with data_col4:
    #st.markdown("### Korteste sti mellom to noder")

    scol1,_, scol2 = st.columns([3,1,3])


    from_word = ""
    to_word = ""

    ws = [x.strip() for x in words.split(',')]

    if len(ws) > 1:
        from_word = ws[0]
        to_word = ws[1]
    else:
        try:
            #cent = pd.DataFrame.from_dict(nx.degree_centrality(Graph), orient='index', columns =['centrality']).sort_values(by='centrality', ascending=False)
            #from_word = cent.iloc[0].name
            #to_word = cent.iloc[1].name
            st.write(ws)
        except:
            pass

    with scol1:
        fra = st.text_input('Fra:', from_word, help = "startnode")
    with scol2:
        til = st.text_input('Til:', to_word, help = "sluttnode")

    if fra != "" and til != "":
        pth = path(Graph, source = fra, target = til)
        st.markdown(f"**{fra} - {til}** {pth[2]}: {', '.join(pth[3])}")
        pth = path(Graph.to_undirected(), source = fra, target = til)
        st.markdown(f"**{fra} - {til}** {pth[2]}: {', '.join(pth[3])}")
        x = len(pth) 
        st.markdown("### Flere stier")
        pth = path(Graph, source = fra, target = til)
        st.markdown(f"**{fra} - {til}** {pth[2]}: {', '.join(pth[3])}")
        pth = path(Graph.to_undirected(), source = fra, target = til)
        st.markdown(f"**{fra} - {til}** {pth[2]}: {', '.join(pth[3])}")