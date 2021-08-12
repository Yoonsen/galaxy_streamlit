import streamlit as st
import dhlab.graph_networkx_louvain as gnl
import pandas as pd
import networkx as nx
from PIL import Image

@st.cache(suppress_st_warning=True, show_spinner = False)
def galaxy(word, lang='nob', cutoff = 16):
    res = nb.unigram(word, ddk = ddk, topic = subject, period = period)
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
st.markdown('Se mer om å drive analytisk DH på [DHLAB-siden](https://nbviewer.jupyter.org/github/DH-LAB-NB/DHLAB/blob/master/DHLAB_ved_Nasjonalbiblioteket.ipynb), og korpusanalyse via web [her](https://beta.nb.no/korpus/)')


st.title('Galakser')


#ax = df.plot(figsize = (10,6 ), lw = 5, alpha=0.8)
#ax.spines["top"].set_visible(False)
#ax.spines["right"].set_visible(False)

#ax.spines["bottom"].set_color("grey")
#ax.spines["left"].set_color("grey")
#ax.spines["bottom"].set_linewidth(3)
#ax.spines["left"].set_linewidth(3)
#ax.legend(loc='upper left', frameon=False)
#ax.spines["left"].set_visible(False)
#st.pyplot()
st.line_chart(df)

#st.line_chart(tot)


#if st.button('Sjekk fordeling i bøker'):
if antall > 0:
    
    wordlist = allword
    
    urns = {w:nb.book_urn(words=[w], ddk = ddk, period = (period_slider[0], period_slider[1]), limit = antall) for w in wordlist}
    #data = {w: nb.aggregate_urns(urns[w]) for w in wordlist}
    #st.write([(w,urns[w]) for w in wordlist])
    urner = lambda w: [x[0] for x in urns[w]]
    #st.write(urner(wordlist[0]))
    data = {'bok ' + w:nb.word_freq(urner(w), wordlist) for w in wordlist}

    st.markdown("### Bøker som inneholder en av _{ws}_ i kolonnene, ordfrekvens i radene".format(ws = ', '.join(wordlist)))
    
    st.write('En diagonal indikerer at ordene gjensidig utelukker hverandre')
    
    st.write(nb.frame(data).transpose().fillna(0))

    #st.write(df.loc[wordlist].fillna(0))
