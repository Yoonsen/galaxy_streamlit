import streamlit as st
import dhlab.nbtext as nb
import gnl as gnl
import pandas as pd

import pyvis as pv
from pyvis.network import Network

import streamlit.components.v1 as components

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
    cent = nx.degree_centrality(g)
    for i in g.nodes(data = True):
        nodes.append(Node(id=i[0], label=i[0], size=100*cent[i[0]], color=cmap[i[0]]) )
    for i in g.edges(data = True):
        edges.append(Edge(source=i[0], target=i[1], type="CURVE_SMOOTH", color = "#ADD8E6"))

    config = Config(
        width=1500, height=1000,
        directed=False,
        physics = True,
        chargeStrength=-200,  # Increased repulsive force
        linkDistance=30,      # Longer links to spread out nodes
        # Note: There may not be a direct collision force parameter
)
    
    
    return nodes, edges, config



def create_pyvis_graph(g, community_dict):
    """
    Create a pyvis graph from a networkx graph.
    
    Parameters:
    - g: A NetworkX graph.
    - community_dict: A dictionary mapping node identifiers to community identifiers.
    
    Returns:
    A pyvis Network object.
    """
    # Create a new pyvis Network. You might want to adjust the width and height to fit your Streamlit app's layout.
    net = Network(height="1000px", width="100%", bgcolor="white", font_color="black")

    # Optional: Adjust physics settings to your liking
    net.barnes_hut(gravity=-80000, central_gravity=0.3, spring_length=100, spring_strength=0.01, damping=0.09, overlap=0)

    # Map community to colors
    cmap = word_to_colors(community_dict)

    # Add nodes with attributes
    for node, attrs in g.nodes(data=True):
        size = 300 * nx.degree_centrality(g).get(node, 0.1)  # Adjust the size based on degree centrality
        color = cmap.get(node, "#ADD8E6")  # Default color if not found in cmap
        title = f"Node: {node}"  # You can add more node-specific information here
        font_dict = {"size": 650, "face": "arial", "color": "black"}
        net.add_node(node, title=title, size=size, color=color, font=font_dict)
    # Add edges
    for source, target, attrs in g.edges(data=True):
        # If you have edge weights or other attributes, you can modify the title or value accordingly
        title = f"{source} -> {target}"
        net.add_edge(source, target, title=title, color="#ADD8E6")

    # Set some additional network properties if needed
    net.set_options("""
    var options = {
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -80000,
          "centralGravity": 0.3,
          "springLength": 0.1,
          "springConstant": 0.04,
          "damping": 0.09,
          "avoidOverlap": 0
        },
        "minVelocity": 0.75
      }
    }
    """)

    return net


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

Graph, comm, cliques = galaxy(words, lang = 'nob', cutoff = cutoff, corpus = corpus)
#nodes, edges, config = create_nodes_and_edges_config(Graph, comm)


with data_col1:

    fig, ax = plt.subplots()
    if nx.is_empty(Graph):
        st.write(" -- ingen treff --")
    else:

        net = create_pyvis_graph(Graph, comm)
        
        # Save the network to an HTML file and read the HTML
        net.save_graph("temp_graph.html")
        with open("temp_graph.html", "r") as f:
            html_string = f.read()
        
        # Use Streamlit's HTML component to display the graph
        components.html(html_string, height=1000)

        #st.write("### Graf")
        
        # plot fra dhlab
        #gnl.show_graph(Graph, spread = 1.2, fontsize = 12, show_borders = [])
        #st.pyplot(fig)
        
        # plot med d3
        #agraph(nodes, edges, config)
        

with data_col2:
    #------------------------------------------ Clustre -------------------------------###

    #st.write('### Clustre')
    st.write('\n\n'.join(['**{label}** {value}'.format(label = key, value = ', '.join(comm[key])) for key in comm]))


    #----------------------------------------- cent

with data_col3:
    #st.write('### Klikkstruktur')

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
            cent = pd.DataFrame.from_dict(nx.degree_centrality(Graph), orient='index', columns =['centrality']).sort_values(by='centrality', ascending=False)
            from_word = cent.iloc[0].name
            to_word = cent.iloc[1].name
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