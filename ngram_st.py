import streamlit as st
import dhlab.nbtext as nb
import pandas as pd
from PIL import Image

@st.cache(suppress_st_warning=True, show_spinner = False)
def ngram(word, ddk, subject, period):
    if " " in word:
        bigram = word.split()[:2]
        res = nb.bigram(first = bigram [0], second = bigram [1], ddk = ddk, topic = subject, period = period)
    else:
        res = nb.unigram(word, ddk = ddk, topic = subject, period = period)
    return res

@st.cache(suppress_st_warning=True, show_spinner = False)
def sumword(words, ddk, topic, period):
    wordlist =   [x.strip() for x in words.split(',')]
    # check if trailing comma, or comma in succession, if so count comma in
    if '' in wordlist:
        wordlist = [','] + [y for y in wordlist if y != '']
    ref = pd.concat([nb.unigram(w, ddk = ddk, topic = topic, period = period) for w in wordlist], axis = 1).sum(axis = 1)
    ref.columns = ["tot"]
    return ref



image = Image.open('NB-logo-no-eng-svart.png')
st.image(image, width = 200)
st.markdown('Se mer om å drive analytisk DH på [DHLAB-siden](https://nbviewer.jupyter.org/github/DH-LAB-NB/DHLAB/blob/master/DHLAB_ved_Nasjonalbiblioteket.ipynb), og korpusanalyse via web [her](https://beta.nb.no/korpus/)')


st.title('Ord og bigram')

st.markdown('### Trendlinjer')

st.sidebar.header('Input')
words = st.text_input('Fyll inn ord eller bigram adskilt med komma. Det skilles mellom store og små bokstaver', "")
if words == "":
    words = "det"

sammenlign = st.sidebar.text_input("Sammenling med summen av følgende ord - sum av komma og punktum er standard, som gir tilnærmet 10nde-del av inputordenes relativfrekvens", ".,")
 
allword = list(set([w.strip() for w in words.split(',')]))[:30]

st.sidebar.header('Parametre fra metadata')
st.sidebar.subheader('Dewey')
st.sidebar.markdown("Se definisjoner av [Deweys desimalkoder](https://deweysearchno.pansoft.de/webdeweysearch/index.html).")
ddk = st.sidebar.text_input('Skriv bare de første sifrene, for eksempel 8 for alle nummer som starter med 8, som gir treff på all kodet skjønnlitteratur.', "")
if ddk == "":
    ddk = None

if ddk != None and not ddk.endswith("%"):
    ddk = ddk + "%"
st.sidebar.subheader('Temaord')
subject = st.sidebar.text_input('Temaord fra Nasjonalbibliografien - Marc21 felt 655 (stor forbokstav) eller felt 653 (liten forbokstav) - merk forskjell på urfolk og Urfolk', '')
if subject == '':
    subject = None
    
st.sidebar.subheader('Tidsperiode')
period_slider = st.sidebar.slider(
    'Angi periode - år mellom 1900 og 2014',
    1900, 2020, (1950, 2010)
)

# wrapper for nb.frame() check if dataframe is empty before assigning names to columns
def frm(x, y):
    if not x.empty:
        res = nb.frame(x, y)
    else:
        res = x
    return res

st.sidebar.header('Visning')
smooth_slider = st.sidebar.slider('Glatting', 1, 8, 3)

st.sidebar.header('Fordeling i bøker')
#antall = st.sidebar.number_input( "For sjekking av fordeling i bøker - jo fler jo lenger ventetid, forskjellige søk vil vanligvis gi nye bøker", 10)
st.sidebar.markdown("For sjekking av fordeling i bøker - sett verdien til større enn null for å sjekke")
antall = st.sidebar.number_input("Antall bøker", 0, 100, 0)

df = pd.concat([frm(ngram(word, ddk = ddk, subject = subject, period = (period_slider[0], period_slider[1])), word) for word in allword], axis=1)



# Råfrekvenser unigram
if sammenlign != "":
    tot = sumword(sammenlign, ddk, subject, period=(period_slider[0], period_slider[1]))
    for x in df:
        df[x] = df[x]/tot

df = df.rolling(window= smooth_slider).mean()
df.index = pd.to_datetime(df.index, format='%Y')

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
