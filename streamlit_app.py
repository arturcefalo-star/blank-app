import streamlit as st
import time
import random
from streamlit_autorefresh import st_autorefresh

if "mostrar_foto" not in st.session_state:
    st.session_state.mostrar_foto = False
if "pontos" not in st.session_state:
    st.session_state.pontos = 0
if "foto_sorteada" not in st.session_state:
    st.session_state.foto_sorteada = None
if "sorteado" not in st.session_state:
    st.session_state.sorteado = True
if "poder_base" not in st.session_state:
    st.session_state.poder_base = 1

col3, col4, col5, col6 = st.columns(4)

if "pontos" not in st.session_state:
    st.session_state.pontos = 0
if "poder_clique" not in st.session_state:
    st.session_state.poder_clique = 1
if "pontos_por_segundo" not in st.session_state:
    st.session_state.pontos_por_segundo = 0
if "ultimo_tick" not in st.session_state:
    st.session_state.ultimo_tick = time.time()

def comprar_melhoria(custo, tipo, qtd):
    if st.session_state.pontos >= custo:
        st.session_state.pontos = max(0, st.session_state.pontos - custo)
        if tipo == "clique":
            st.session_state.poder_clique += qtd
        elif tipo == "passivo":
            st.session_state.pontos_por_segundo += qtd 
        time.sleep(0.5)
        st.rerun()

if st.session_state.pontos_por_segundo > 0:
    st_autorefresh(interval=900, key="autoclicker")

agora = time.time()
tempo_passado = agora - st.session_state.ultimo_tick

if tempo_passado >= 1.0:
    ciclos = int(tempo_passado)
    st.session_state.pontos += st.session_state.pontos_por_segundo * ciclos
    st.session_state.ultimo_tick = agora - (tempo_passado - ciclos)
def adicionar_ponto():
    st.session_state.pontos += st.session_state.poder_clique

#COLUNA 
melhorias_clique = [
    {"qtd": 1, "custo": 100},
    {"qtd": 5, "custo": 500},
    {"qtd": 10, "custo": 1000},
    {"qtd": 50, "custo": 5000},
    {"qtd": 100, "custo": 10000},
    {"qtd": 500, "custo": 50000},
    {"qtd": 1000, "custo": 100000},
    {"qtd": 2500, "custo": 250000},
    {"qtd": 5000, "custo": 500000},
    {"qtd": 10000, "custo": 1000000},
]

#COLUNA 2
melhorias_passivas = [
    {"qtd": 5, "custo": 200},
    {"qtd": 10, "custo": 600},
    {"qtd": 20, "custo": 1100},
    {"qtd": 100, "custo": 7500},
    {"qtd": 200, "custo": 14500},
    {"qtd": 1000, "custo": 72500},
]

st.title("Clicker Game (Beta)")
st.write("Trilha sonora: on/off ")
st.audio("musica67.mp3")

if st.button("            Click Here          "):
    st.session_state.pontos += st.session_state.poder_clique

st.write(f"Pontos: {st.session_state.pontos}")
st.write(f"Poder de clique: {st.session_state.poder_clique}")
st.write(f"Pontos por segundo: {st.session_state.pontos_por_segundo}")

with col3:
    if st.button("Abrir Ovo = 100 Pontos"):
        if st.session_state.pontos >= 100:
            st.session_state.pontos -= 100

            sorteado = random.choices(
               [{"nome": "Siruriru", "arquivo": "logo3.png", "bonus": 1, "chance": "50%"}, 
                {"nome": "Peppa Pig", "arquivo": "logo2.png", "bonus": 5, "chance": "35%"},
                {"nome": "Manoel G", "arquivo": "logo1.png", "bonus": 10, "chance": "15%"}],
               weights = [50, 35, 15], k=1
            )[0]
            st.session_state.foto_sorteada = sorteado

            st.session_state.poder_clique = st.session_state.poder_base + sorteado["bonus"]
        else:
            st.warning("Pontos insuficiente")

    if "foto_sorteada" in st.session_state and st.session_state.foto_sorteada:
        ganhou = st.session_state.foto_sorteada

        if "arquivo" in ganhou:
            st.write(f"Seus Pets:")
            st.image(ganhou["arquivo"], width=100)
            st.write(f"{ganhou.get('chance')} - {ganhou['nome']} + {ganhou.get('bonus')} Ponto(s)")

st.markdown("---")

col1, col2 = st.columns(2)

#COLUNA 1:
with col1:
    st.subheader("Melhoria Clicker")
    for item in melhorias_clique:
        texto = f"Melhoria +{item['qtd']} = {item['custo']} Pontos"

        desativado = st.session_state.pontos < item['custo']

        if st.button(texto, key=f"clique_{item['qtd']}", disabled=desativado):
            time.sleep(0.1) 
            if st.session_state.pontos >= item['custo']:
                st.session_state.pontos -= item['custo']
                st.session_state.poder_clique += item['qtd']
                st.rerun()
            else:
                st.warning("Pontos insuficiente")

with col2:
    st.subheader("Auto Clickers")
    for item in melhorias_passivas:
        texto = f"Gerador +{item['qtd']}/s = {item['custo']} Pontos"

        desativado = st.session_state.pontos < item['custo']

        if st.button(texto, key=f"passivo_{item['qtd']}", disabled=desativado):
            time.sleep(0.1)
            if st.session_state.pontos >= item['custo']:
                st.session_state.pontos -= item['custo']
                st.session_state.pontos_por_segundo += item['qtd']
                st.rerun()
            else:
                st.warning("Pontos insuficiente")
