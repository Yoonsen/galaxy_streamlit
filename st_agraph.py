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
url = "https://beta.nb.no/dhlab/galaxies/query"

def create_nodes_and_edges_config(g):
    """create nodes and edges from a networkx graph for streamlit agraph, classes Nodes, Edges and Config must be imported"""
    nodes = []
    edges = []
    for i in g.nodes(data = True):
        nodes.append(Node(id=i[0], size=100) )
    for i in g.edges(data = True):
        edges.append(Edge(source=i[0], target=i[1], type="CURVE_SMOOTH", color = "blue"))

    config = Config(height=500,
                width=700, 
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
            edgelist += [(nodes[edge['source']]['name'], nodes[edge['target']]['name'], abs(edge['value']))]
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

@st.cache(suppress_st_warning=True, show_spinner = False)
def show_data(data):
    fontsize = 12

    fig, ax = plt.subplots() #nrows=2, ncols=2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.spines["bottom"].set_color("grey")
    ax.spines["left"].set_color("grey")
    ax.spines["bottom"].set_linewidth(0.5)
    ax.spines["left"].set_linewidth(0.3)
    ax.legend(loc='upper left', frameon=False)
    ax.spines["left"].set_visible(False)

    plt.rcParams.update({'font.size': 12,
                        'font.family': 'monospace',
                        'font.monospace':'Courier'})

    plt.legend(loc = 2, prop = {
        'size': fontsize})
    #plt.xlabel('Ordliste', fontsize= fontsize*0.8)
    #plt.ylabel('Frekvensvekt', fontsize= fontsize*0.8)
    data.plot(ax=ax, figsize = (8,4), kind='bar', rot=20)

    st.pyplot(fig)

    st.write('som tabell')
    st.write(data.style.background_gradient())

    

image = Image.open('NB-logo-no-eng-svart.png')
st.image(image, width = 200)
st.markdown("""Les mer om DH på [DHLAB-siden](https://nbviewer.jupyter.org/github/DH-LAB-NB/DHLAB/blob/master/DHLAB_ved_Nasjonalbiblioteket.ipynb), og korpusanalyse via web [her](https://beta.nb.no/korpus/)

Data er hentet fra NBs trigrambase for norsk, og fra Googles trigrambase for engelsk og tysk""")


st.title('Ordnettverk')

#st.sidebar.title('Parametre')
cutoff = st.sidebar.number_input('Cutoff', min_value = 12, max_value =24, value = 16)
lang = st.sidebar.selectbox('Språk-kode',['nob', 'eng', 'ger'])
fontsize = st.sidebar.number_input('Fontstørrelse', min_value = 0, max_value = 32, value = 12)
spread = st.sidebar.number_input('Spredning av grafen', min_value = 0.0, max_value = 2.6, value = 1.2)
centrality_size = st.sidebar.number_input('Sentralitet', min_value = 10, max_value = 100, value = 12)
node_number = st.sidebar.number_input('Vis antall noder ved tekstvisning', min_value = 5, value = 50)
show_graph = st.sidebar.checkbox('Tegn grafen', value = True)
corpus = st.sidebar.selectbox('Bøker eller aviser', ['bok', 'avis', 'begge'])
if corpus == 'begge':
    corpus = 'all'

words = st.text_input('Skriv inn ett ord eller flere adskilt med komma', 'demokrati')

Graph, comm, cliques = galaxy(words, lang = lang, cutoff = cutoff, corpus = corpus)

fig, ax = plt.subplots()
if nx.is_empty(Graph):
    st.write("tom graf")
elif show_graph:
    #gnl.show_graph(Graph, spread = spread, fontsize = fontsize, show_borders = [])
    #st.pyplot(fig)
    nodes, edges, config = create_nodes_and_edges_config(Graph)
    agraph(nodes, edges, config)
else:
    nodes = list(Graph.nodes)
    st.write(f'Det er totalt {len(nodes)} noder i grafen')
    st.markdown(f"""En liste av inntil {min(node_number, len(nodes))} noder:
                {', '.join(nodes[:node_number])}""")


#------------------------------------------- Path ---------------------------------###############

st.markdown("### Korteste sti")
fra = st.text_input('Fra:', "")
til = st.text_input('Til:', "")
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
    
    


#------------------------------------------ Clustre -------------------------------###

st.write('### Clustre')
st.write('\n\n'.join(['**{label}** {value}'.format(label = key, value = ', '.join(comm[key])) for key in comm]))


#----------------------------------------- cent

st.write('### Sentralitet')
st.write(
    pd.DataFrame(
        {
            'betweenness':{x[0]:x[1] for x in nb.central_betweenness_characters(Graph, n = centrality_size)},
            'centrality':{x[0]:x[1] for x in nb.central_characters(Graph, n = centrality_size)}
        }
    ).style.background_gradient()
)

st.write('### klikkstruktur')

st.write('\n\n'.join(["{a}: {b}".format(a = '-'.join([str(x) for x in key]), b = ', '.join(cliques[key])) for key in cliques]))
