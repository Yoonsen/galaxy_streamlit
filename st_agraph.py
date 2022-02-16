import streamlit as st
import dhlab.nbtext as nb
import gnl as gnl
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image
import requests
from streamlit_agraph import agraph, TripleStore, Config, Node, Edge

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


def create_nodes_and_edges_config(g, community_dict):
    """create nodes and edges from a networkx graph for streamlit agraph, classes Nodes, Edges and Config must be imported"""
    cmap = word_to_colors(community_dict)
    nodes = []
    edges = []
    for i in g.nodes(data = True):
        nodes.append(Node(id=i[0], size=100, color=cmap[i[0]]) )
    for i in g.edges(data = True):
        edges.append(Edge(source=i[0], target=i[1], type="CURVE_SMOOTH", color = "#ADD8E6"))

    config = Config(height=500,
                nodeHighlightBehavior=True,
                highlightColor="#F7A7A6", 
                directed=True, 
                collapsible=True)
    
    return nodes, edges, config


@st.cache(suppress_st_warning=True, show_spinner = False)
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

@st.cache(suppress_st_warning=True, show_spinner = False)
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

@st.cache(suppress_st_warning=True, show_spinner = False)
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

@st.cache(suppress_st_warning=True, show_spinner = False, allow_output_mutation = True)
def galaxy(word, lang='nob', corpus = 'all', cutoff = 16):
    if lang == 'nob':
        res = word_graph(word, corpus = corpus, cutoff = cutoff)
    else:
        res = nb.make_graph(word, lang = lang, cutoff = cutoff)
   
    comm = gnl.community_dict(res)
    cliques = gnl.kcliques(res.to_undirected())
    return res, comm, cliques


    
st.set_page_config(layout="wide")

image = Image.open("DHlab_logo_web_en_black.png")
st.sidebar.image(image)
st.sidebar.markdown("""Les mer om DH ved Nasjonalbiblioteket på [DHLAB-siden](https://nb.no/dh-lab)""")


st.title('Ordnettverk')

st.sidebar.title('Parametre')

cutoff = st.sidebar.number_input('Tilfang av noder', min_value = 12, max_value =24, value = 18, 
                                 help="Angi et tall mellom 12 og 24 - jo større, jo fler noder -"
                                 " effektiv kun for norsk 'nob'")

lang = st.sidebar.selectbox('Språk',['nob', 'eng', 'ger'], 
                            help="language code - "
                            "Data for English ('eng') and German ('ger') are fetched from Google trigrams 2013, see Google N-gram viewer https://books.google.com/ngrams")
#fontsize = st.sidebar.number_input('Fontstørrelse', min_value = 0, max_value = 32, value = 12)
#spread = st.sidebar.number_input('Spredning av grafen', min_value = 0.0, max_value = 2.6, value = 1.2)

#centrality_size = st.sidebar.number_input('Størrelse på tabell', min_value = 10, max_value = 500, value = 12, 
#                                          help="How many rows to show in table for sorted centrality")

show_graph = st.sidebar.checkbox('Visualisering av graf', value = True, help="Visualize the graph")

node_number = 50
if not show_graph:
    node_number = st.sidebar.number_input('Antall noder å vise ved tekstvisning', min_value = 5, value = 50, 
                                     help="Specify number of nodes to show if graph is not visualized")



corpus = st.sidebar.selectbox('Bøker eller aviser', ['begge', 'bok', 'avis' ], help="Choose between books and newspapers or both, only for language is norwegian 'nob'")
if corpus == 'begge':
    corpus = 'all'

words = st.text_input('Skriv inn ett ord eller flere adskilt med komma. Det skilles mellom store og små bokstaver', 'frihet')

Graph, comm, cliques = galaxy(words, lang = lang, cutoff = cutoff, corpus = corpus)

fig, ax = plt.subplots()
if nx.is_empty(Graph):
    st.write("tom graf")
elif show_graph:
    #gnl.show_graph(Graph, spread = spread, fontsize = fontsize, show_borders = [])
    #st.pyplot(fig)
    nodes, edges, config = create_nodes_and_edges_config(Graph, comm)
    agraph(nodes, edges, config)
else:
    nodes = list(Graph.nodes)
    st.write(f'Det er totalt {len(nodes)} noder i grafen')
    st.markdown(f"""En liste av inntil {min(node_number, len(nodes))} noder:
                {', '.join(nodes[:node_number])}""")



    


#------------------------------------------ Clustre -------------------------------###

st.write('### Clustre')
st.write('\n\n'.join(['**{label}** {value}'.format(label = key, value = ', '.join(comm[key])) for key in comm]))

#------------------------------------------- Path ---------------------------------###############

st.markdown("### Korteste sti mellom to noder")
fra = st.text_input('Fra:', "", help="startnode")
til = st.text_input('Til:', "", help = "sluttnode")
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
    
#----------------------------------------- cent


st.write('### klikkstruktur')

st.write('\n\n'.join(["{a}: {b}".format(a = '-'.join([str(x) for x in key]), b = ', '.join(cliques[key])) for key in cliques]))
