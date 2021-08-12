import streamlit as st
import dhlab.nbtext as nb
import graph_networkx_louvain as gnl
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image

#@st.cache(suppress_st_warning=True, show_spinner = False)
def galaxy(word, lang='nob', cutoff = 16):
    res = nb.make_graph(word, lang = lang, cutoff = cutoff)
    return res

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
st.markdown("""Se mer om å drive analytisk DH på [DHLAB-siden](https://nbviewer.jupyter.org/github/DH-LAB-NB/DHLAB/blob/master/DHLAB_ved_Nasjonalbiblioteket.ipynb), og korpusanalyse via web [her](https://beta.nb.no/korpus/)

Data er hentet fra NBs trigrambase for norsk, og fra Googles trigrambase for engelsk og tysk""")


st.title('Galakser')

#st.sidebar.title('Parametre')
cutoff = st.sidebar.number_input('cutoff', min_value = 12, max_value =24, value = 16)
lang = st.sidebar.selectbox('lang',['nob', 'eng', 'ger'])
fontsize = st.sidebar.number_input('fontsize', min_value = 0, max_value = 32, value = 12)
spread = st.sidebar.number_input('spread', min_value = 0.0, max_value = 2.6, value = 1.2)


words = st.text_input('Ord adskilt med komma', 'demokrati')

Graph = galaxy(words, lang = lang, cutoff = cutoff)
fig, ax = plt.subplots()

if nx.is_empty(Graph):
    st.write("tom graf")
else:
    gnl.show_graph(Graph, spread = spread, fontsize = fontsize)
    st.pyplot(fig)

comm = gnl.community_dict(Graph)
st.write('\n\n'.join(['**{label}** {value}'.format(label = key, value = ', '.join(comm[key])) for key in comm]))
#st.write(gnl.show_cliques(Graph))