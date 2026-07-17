import streamlit as st
import time
import random
from streamlit_autorefresh import st_autorefresh

# 1. INICIALIZAÇÃO DO ESTADO (SESSION STATE)
if "pontos" not in st.session_state:
    st.session_state.pontos = 0
if "poder_base" not in st.session_state:
    st.session_state.poder_base = 1
if "poder_clique" not in st.session_state:
    st.session_state.poder_clique = 1
if "pontos_por_segundo" not in st.session_state:
    st.session_state.pontos_por_segundo = 0
if "ultimo_tick" not in st.session_state:
    st.session_state.ultimo_tick = time.time()

# Guardar os pets equipados em cada slot
if "pet_slot_1" not in st.session_state:
    st.session_state.pet_slot_1 = None
if "pet_slot_2" not in st.session_state:
    st.session_state.pet_slot_2 = None

if "ovo1_bloqueado" not in st.session_state:
    st.session_state.ovo1_bloqueado = False

# 2. SISTEMA DE REFRESH PASSIVO (AUTO-CLICKER)
if st.session_state.pontos_por_segundo > 0:
    st_autorefresh(interval=900, key="autoclicker")

agora = time.time()
tempo_passado = agora - st.session_state.ultimo_tick

if tempo_passado >= 1.0:
    ciclos = int(tempo_passado)
    st.session_state.pontos += st.session_state.pontos_por_segundo * ciclos
    st.session_state.ultimo_tick = agora - (tempo_passado - ciclos)

# Função para recalcular o poder de clique com base no poder base + pets equipados
def atualizar_poder_clique():
    bonus_total = 0
    if st.session_state.pet_slot_1:
        bonus_total += st.session_state.pet_slot_1["bonus"]
    if st.session_state.pet_slot_2:
        bonus_total += st.session_state.pet_slot_2["bonus"]
    st.session_state.poder_clique = st.session_state.poder_base + bonus_total

# 3. INTERFACE PRINCIPAL
st.title("Clicker Game")

st.write("Trilha sonora: on/off ")
st.audio("musica67.mp3")

# Botão principal de clique
if st.button("            Click Here          ", use_container_width=True):
    st.session_state.pontos += st.session_state.poder_clique

# Exibição de Status
st.metric(label="Pontos Atuais", value=st.session_state.pontos)
col_status1, col_status2 = st.columns(2)
col_status1.write(f"**Poder de clique:** {st.session_state.poder_clique}")
col_status2.write(f"**Pontos por segundo:** {st.session_state.pontos_por_segundo}")

st.markdown("---")

# 4. SISTEMA DE OVOS (PETS)
st.subheader("Comprar Ovos:")
col3, col4 = st.columns(2)

with col3:
    st.write("### Ovo Comum:")
    st.write("Siruriru: 50% (+1 Ponto)")
    st.write("Peppa Pig: 35% (+5 Pontos)")
    st.write("Manoel G: 15% (+10 Pontos)")
    
    custo_ovo1 = 100
    desativar_ovo1 = st.session_state.ovo1_bloqueado or st.session_state.pontos < custo_ovo1
    
    if st.button(f"Abrir Ovo = {custo_ovo1} Pontos", disabled=desativar_ovo1, key="botao_ovo1"):
        st.session_state.pontos -= custo_ovo1
        sorteado_ovo1 = random.choices(
           [{"nome": "Siruriru", "arquivo": "logo3.png", "bonus": 1, "chance": "50%"}, 
            {"nome": "Peppa Pig", "arquivo": "logo2.png", "bonus": 5, "chance": "35%"},
            {"nome": "Manoel G", "arquivo": "logo1.png", "bonus": 10, "chance": "15%"}],
           weights=[50, 35, 15], k=1
        )[0]
        st.session_state.pet_slot_1 = sorteado_ovo1
        atualizar_poder_clique()
        st.rerun()

    if st.session_state.pet_slot_1:
        pet = st.session_state.pet_slot_1
        st.write("**Pet Equipado:**")
        # PROTEÇÃO DE IMAGEM: Se a imagem não for encontrada, o app exibe um aviso em vez de travar
        try:
            st.image(pet["arquivo"], width=150)
        except Exception:
            st.warning(f"⚠️ Imagem ({pet['arquivo']}) não encontrada na pasta do projeto.")
        st.caption(f"{pet['nome']} ({pet['chance']}) | +{pet['bonus']} por clique")

with col4:
    st.write("### Ovo Raro:")
    st.write("Dora A.: 50% (+10 Pontos)")
    st.write("Sonic: 35% (+50 Pontos)")
    st.write("Michael J.: 15% (+100 Pontos)")
    
    custo_ovo2 = 1000
    desativar_ovo2 = st.session_state.pontos < custo_ovo2
    
    if st.button(f"Abrir Ovo = {custo_ovo2} Pontos", disabled=desativar_ovo2, key="botao_ovo2"):
        st.session_state.pontos -= custo_ovo2
        st.session_state.ovo1_bloqueado = True  # Bloqueia o ovo 1 se desejado por sua mecânica
        
        sorteado_ovo2 = random.choices(
           [{"nome": "Dora A.", "arquivo": "logo4.png", "bonus": 10, "chance": "50%"}, 
            {"nome": "Sonic", "arquivo": "logo5.png", "bonus": 50, "chance": "35%"},
            {"nome": "Michael J.", "arquivo": "logo6.png", "bonus": 100, "chance": "15%"}],
           weights=[50, 35, 15], k=1
        )[0]
        st.session_state.pet_slot_2 = sorteado_ovo2
        atualizar_poder_clique()
        st.rerun()

    if st.session_state.pet_slot_2:
        pet = st.session_state.pet_slot_2
        st.write("**Pet Equipado:**")
        # PROTEÇÃO DE IMAGEM: Se a imagem não for encontrada, o app exibe um aviso em vez de travar
        try:
            st.image(pet["arquivo"], width=150)
        except Exception:
            st.warning(f"⚠️ Imagem ({pet['arquivo']}) não encontrada na pasta do projeto.")
        st.caption(f"{pet['nome']} ({pet['chance']}) | +{pet['bonus']} por clique")

st.markdown("---")

# 5. LOJA DE MELHORIAS (CLIQUE E AUTO-CLICK)
col1, col2 = st.columns(2)

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

melhorias_passivas = [
    {"qtd": 5, "custo": 200},
    {"qtd": 10, "custo": 600},
    {"qtd": 20, "custo": 1100},
    {"qtd": 100, "custo": 7500},
    {"qtd": 200, "custo": 14500},
    {"qtd": 1000, "custo": 72500},
]

with col1:
    st.subheader("Melhoria Clicker")
    for item in melhorias_clique:
        texto = f"Melhoria +{item['qtd']} = {item['custo']} Pts"
        desativado = st.session_state.pontos < item['custo']

        if st.button(texto, key=f"clique_{item['qtd']}", disabled=desativado, use_container_width=True):
            st.session_state.pontos -= item['custo']
            st.session_state.poder_base += item['qtd']
            atualizar_poder_clique()  # Recalcula somando os pets ativos ao novo poder base
            st.rerun()

with col2:
    st.subheader("Auto Clickers")
    for item in melhorias_passivas:
        texto = f"Gerador +{item['qtd']}/s = {item['custo']} Pts"
        desativado = st.session_state.pontos < item['custo']

        if st.button(texto, key=f"passivo_{item['qtd']}", disabled=desativado, use_container_width=True):
            st.session_state.pontos -= item['custo']
            st.session_state.pontos_por_segundo += item['qtd']
            st.rerun()

# 6. LOG DE ATUALIZAÇÕES
st.markdown("---")
st.subheader("Atualizações:")
st.write("(1.0.0)(Beta) - Lançamento!!!")
st.write("(1.0.1) - Correção de bugs")
st.write("(1.1.2) - Adição dos Ovos, correção de bugs e preços balanceados")
st.write("(1.2.3) - Adição de novos pets e ovos e o log de atualizações")
st.write("(1.3.4) - Interface reformulada e correção de bugs")


