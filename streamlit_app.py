import streamlit as st
import time
import random
import json
import os
from streamlit_autorefresh import st_autorefresh

# Arquivos de salvamento
SAVE_FILE = "savegame.json"
LEADERBOARD_FILE = "leaderboard.json"

# --- FUNÇÕES DE SALVAMENTO E LEADERBOARD ---

def salvar_jogo():
    dados = {
        "pontos": st.session_state.pontos,
        "poder_base": st.session_state.poder_base,
        "pontos_por_segundo": st.session_state.pontos_por_segundo,
        "pet_slot_1": st.session_state.pet_slot_1,
        "pet_slot_2": st.session_state.pet_slot_2,
        "ultimo_tick": st.session_state.ultimo_tick,
        "ja_enviou": st.session_state.ja_enviou,
        "nome_usuario": st.session_state.nome_usuario
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def carregar_jogo():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def carregar_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                dados = json.load(f)
            
            usuarios_unicos = {}
            for jogador in dados:
                nome = jogador["Jogador"]
                pontos = jogador.get("Pontos", jogador.get("Points", 0))
                
                if nome.lower() not in usuarios_unicos or pontos > usuarios_unicos[nome.lower()]["Pontos"]:
                    usuarios_unicos[nome.lower()] = {"Jogador": nome, "Pontos": pontos}
            
            return sorted(usuarios_unicos.values(), key=lambda x: x["Pontos"], reverse=True)[:5]
        except Exception:
            return []
    return []

def remover_jogador_leaderboard(nome_antigo):
    if nome_antigo and os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                dados = json.load(f)
            novo_leaderboard = [j for j in dados if j["Jogador"].lower() != nome_antigo.lower()]
            with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
                json.dump(novo_leaderboard, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

def salvar_no_leaderboard(nome, pontos):
    leaderboard = []
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                leaderboard = json.load(f)
        except Exception:
            leaderboard = []
    
    jogador_encontrado = False
    for jogador in leaderboard:
        if jogador["Jogador"].lower() == nome.lower():
            jogador_encontrado = True
            if pontos > jogador["Pontos"]:
                jogador["Pontos"] = pontos
                jogador["Jogador"] = nome 
            break
            
    if not jogador_encontrado:
        leaderboard.append({"Jogador": nome, "Pontos": pontos})
        
    leaderboard = sorted(leaderboard, key=lambda x: x["Pontos"], reverse=True)[:5]
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(leaderboard, f, ensure_ascii=False, indent=4)
    return leaderboard

# --- 1. INICIALIZAÇÃO CORRETA E SEGURA DO ESTADO ---
dados_salvos = carregar_jogo()
if dados_salvos is None:
    dados_salvos = {}

if "pontos" not in st.session_state:
    st.session_state.pontos = dados_salvos.get("pontos", 0)
if "poder_base" not in st.session_state:
    st.session_state.poder_base = dados_salvos.get("poder_base", 1)
if "poder_clique" not in st.session_state:
    st.session_state.poder_clique = 1  
if "pontos_por_segundo" not in st.session_state:
    st.session_state.pontos_por_segundo = dados_salvos.get("pontos_por_segundo", 0)
if "ultimo_tick" not in st.session_state:
    st.session_state.ultimo_tick = dados_salvos.get("ultimo_tick", time.time())
if "ja_enviou" not in st.session_state:
    st.session_state.ja_enviou = dados_salvos.get("ja_enviou", False)
if "nome_usuario" not in st.session_state:
    st.session_state.nome_usuario = dados_salvos.get("nome_usuario", "")

if "ultima_compra" not in st.session_state:
    st.session_state.ultima_compra = 0.0
if "confirmando_reset" not in st.session_state:
    st.session_state.confirmando_reset = False

if "pet_slot_1" not in st.session_state:
    st.session_state.pet_slot_1 = dados_salvos.get("pet_slot_1", None)
if "pet_slot_2" not in st.session_state:
    st.session_state.pet_slot_2 = dados_salvos.get("pet_slot_2", None)

def atualizar_poder_clique():
    bonus_total = 0
    if st.session_state.pet_slot_1:
        bonus_total += st.session_state.pet_slot_1["bonus"]
    if st.session_state.pet_slot_2:
        bonus_total += st.session_state.pet_slot_2["bonus"]
    st.session_state.poder_clique = st.session_state.poder_base + bonus_total

atualizar_poder_clique()

# --- 2. SISTEMA DE REFRESH PASSIVO (AUTO-CLICKER) ---
if st.session_state.pontos_por_segundo > 0:
    st_autorefresh(interval=900, key="autoclicker")

agora = time.time()
tempo_passado = agora - st.session_state.ultimo_tick

if tempo_passado >= 1.0:
    ciclos = int(tempo_passado)
    st.session_state.pontos += st.session_state.pontos_por_segundo * ciclos
    st.session_state.ultimo_tick = agora - (tempo_passado - ciclos)
    salvar_jogo()

loja_em_cooldown = (time.time() - st.session_state.ultima_compra) < 0.5

# --- 3. INTERFACE PRINCIPAL ---
st.title("Clicker Game")

st.write("Trilha sonora: on/off ")
try:
    st.audio("musica67.mp3")
except Exception:
    st.caption("🎵 Arquivo 'musica67.mp3' não encontrado.")

if st.button("            Click Here          ", use_container_width=True):
    st.session_state.pontos += st.session_state.poder_clique
    salvar_jogo()

st.metric(label="Pontos Atuais", value=st.session_state.pontos)
col_status1, col_status2 = st.columns(2)
col_status1.write(f"**Poder de clique:** {st.session_state.poder_clique}")
col_status2.write(f"**Pontos por segundo:** {st.session_state.pontos_por_segundo}")

st.markdown("---")

# --- 4. SISTEMA DE OVOS (PETS) ---
st.subheader("Comprar Ovos:")
col3, col4 = st.columns(2)

with col3:
    st.write("### Ovo Comum:")
    st.write("Siruriru: 50% (+1 Ponto)")
    st.write("Peppa Pig: 35% (+5 Pontos)")
    st.write("Manoel G: 15% (+10 Pontos)")
    
    custo_ovo1 = 100
    desativar_ovo1 = st.session_state.pontos < custo_ovo1 or loja_em_cooldown
    
    if st.button(f"Abrir Ovo = {custo_ovo1} Pontos", disabled=desativar_ovo1, key="botao_ovo1"):
        st.session_state.ultima_compra = time.time()  
        if st.session_state.pontos >= custo_ovo1:
            st.session_state.pontos -= custo_ovo1
            sorteado_ovo1 = random.choices(
               [{"nome": "Siruriru", "arquivo": "logo3.png", "bonus": 1, "chance": "50%"}, 
                {"nome": "Peppa Pig", "arquivo": "logo2.png", "bonus": 5, "chance": "35%"},
                {"nome": "Manoel G", "arquivo": "logo1.png", "bonus": 10, "chance": "15%"}],
               weights=[50, 35, 15], k=1
            )[0]
            st.session_state.pet_slot_1 = sorteado_ovo1
            atualizar_poder_clique()
            salvar_jogo()
            time.sleep(0.5) 
            st.rerun()

    if st.session_state.pet_slot_1:
        pet = st.session_state.pet_slot_1
        st.write("**Pet Equipado:**")
        try:
            st.image(pet["arquivo"], width=150)
        except Exception:
            st.warning(f"⚠️ Imagem ({pet['arquivo']}) não encontrada.")
        st.caption(f"{pet['nome']} ({pet['chance']}) | +{pet['bonus']} por clique")

with col4:
    st.write("### Ovo Raro:")
    st.write("Dora A.: 50% (+10 Pontos)")
    st.write("Sonic: 35% (+50 Pontos)")
    st.write("Michael J.: 15% (+100 Pontos)")
    
    custo_ovo2 = 1000
    desativar_ovo2 = st.session_state.pontos < custo_ovo2 or loja_em_cooldown
    
    if st.button(f"Abrir Ovo = {custo_ovo2} Pontos", disabled=desativar_ovo2, key="botao_ovo2"):
        st.session_state.ultima_compra = time.time()
        if st.session_state.pontos >= custo_ovo2:
            st.session_state.pontos -= custo_ovo2
            sorteado_ovo2 = random.choices(
               [{"nome": "Dora A.", "arquivo": "logo4.png", "bonus": 10, "chance": "50%"}, 
                {"nome": "Sonic", "arquivo": "logo5.png", "bonus": 50, "chance": "35%"},
                {"nome": "Michael J.", "arquivo": "logo6.png", "bonus": 100, "chance": "15%"}],
               weights=[50, 35, 15], k=1
            )[0]
            st.session_state.pet_slot_2 = sorteado_ovo2
            atualizar_poder_clique()
            salvar_jogo()
            time.sleep(0.5) 
            st.rerun()

    if st.session_state.pet_slot_2:
        pet = st.session_state.pet_slot_2
        st.write("**Pet Equipado:**")
        try:
            st.image(pet["arquivo"], width=150)
        except Exception:
            st.warning(f"⚠️ Imagem ({pet['arquivo']}) não encontrada.")
        st.caption(f"{pet['nome']} ({pet['chance']}) | +{pet['bonus']} por clique")

st.markdown("---")

# --- 5. LOJA DE MELHORIAS ---
col1, col2 = st.columns(2)

melhorias_clique = [
    {"qtd": 1, "custo": 100}, {"qtd": 5, "custo": 500}, {"qtd": 10, "custo": 1000},
    {"qtd": 50, "custo": 5000}, {"qtd": 100, "custo": 10000}, {"qtd": 500, "custo": 50000},
    {"qtd": 1000, "custo": 100000}, {"qtd": 2500, "custo": 250000}, {"qtd": 5000, "custo": 500000},
    {"qtd": 10000, "custo": 1000000},
]

melhorias_passivas = [
    {"qtd": 5, "custo": 200}, {"qtd": 10, "custo": 600}, {"qtd": 20, "custo": 1100},
    {"qtd": 100, "custo": 7500}, {"qtd": 200, "custo": 14500}, {"qtd": 1000, "custo": 72500},
    {"qtd": 2000, "custo": 145000}, {"qtd": 5000, "custo": 360000}, {"qtd": 10000, "custo": 725000},
    {"qtd": 20000, "custo": 1450000},
]

with col1:
    st.subheader("Melhoria Clicker")
    for item in melhorias_clique:
        texto = f"Melhoria +{item['qtd']} = {item['custo']} Pts"
        desativado = st.session_state.pontos < item['custo'] or loja_em_cooldown

        if st.button(texto, key=f"clique_{item['qtd']}", disabled=desativado, use_container_width=True):
            st.session_state.ultima_compra = time.time()
            if st.session_state.pontos >= item['custo']: 
                st.session_state.pontos -= item['custo']
                st.session_state.poder_base += item['qtd']
                atualizar_poder_clique()  
                salvar_jogo()
                time.sleep(0.5) 
                st.rerun()

with col2:
    st.subheader("Auto Clickers")
    for item in melhorias_passivas:
        texto = f"Gerador +{item['qtd']}/s = {item['custo']} Pts"
        desativado = st.session_state.pontos < item['custo'] or loja_em_cooldown

        if st.button(texto, key=f"passivo_{item['qtd']}", disabled=disabled, use_container_width=True):
            st.session_state.ultima_compra = time.time()
            if st.session_state.pontos >= item['custo']: 
                st.session_state.pontos -= item['custo']
                st.session_state.pontos_por_segundo += item['qtd']
                salvar_jogo()
                time.sleep(0.5) 
                st.rerun()

# --- 6. LOG DE ATUALIZAÇÕES ---
st.markdown("---")
st.subheader("Atualizações:")
st.write("(1.0.0)(Beta) - Lançamento!!!")
st.write("(1.4.5) - Sistema de salvamento de jogo, autoclickers e botão de reset")
st.write("(1.8.0) - Exclusividade de nomes ativada no Top Global (Bloqueio de nomes duplicados)")
         
# --- 7. TABELA DE CLASSIFICAÇÃO COM VALIDAÇÃO DE UNICIDADE ---
st.markdown("---")
st.subheader("Top 5 global:")

dados_placar = carregar_leaderboard()

nome_input = st.text_input(
    "Digite seu nome para salvar seu recorde:", 
    value=st.session_state.get("nome_usuario", ""), 
    max_chars=15, 
    key="nome_leaderboard_widget"
)

botao_desativado = nome_input.strip() == ""

if st.button("Enviar Pontuação para o Placar", use_container_width=True, disabled=botao_desativado):
    nome_novo = nome_input.strip()
    nome_antigo = st.session_state.nome_usuario
    
    # 1. VERIFICAÇÃO DE UNICIDADE: Checa se o nome digitado já existe no arquivo global
    nome_ja_existe = False
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                todos_jogadores = json.load(f)
            nome_ja_existe = any(j["Jogador"].lower() == nome_novo.lower() for j in todos_jogadores)
        except Exception:
            pass

    # 2. SE O NOME JÁ EXISTE: Só permite se pertencer à própria pessoa tentando atualizar
    if nome_ja_existe and nome_novo.lower() != nome_antigo.lower():
        st.error("❌ Esse nome já está sendo utilizado por outro jogador!")
    else:
        # Se for uma troca válida de nome próprio, remove o nome antigo da tabela primeiro
        if nome_antigo != "" and nome_novo.lower() != nome_antigo.lower():
            remover_jogador_leaderboard(nome_antigo)
        
        st.session_state.nome_usuario = nome_novo
        st.session_state.ja_enviou = True  
        
        dados_placar = salvar_no_leaderboard(nome_novo, st.session_state.pontos)
        salvar_jogo()  
        st.success(f"Placar atualizado com sucesso como: {nome_novo}")
        time.sleep(0.5)
        st.rerun()

if dados_placar:
    st.table(dados_placar)
else:
    st.info("O placar está vazio. Seja o primeiro a registrar um recorde!")

# --- 8. SISTEMA DE RESET DE JOGO ---
st.markdown("---")
if not st.session_state.confirmando_reset:
    if st.button("Resetar Jogo", use_container_width=True):
        st.session_state.confirmando_reset = True
        st.rerun()
else:
    st.warning("⚠️ **Você tem certeza absoluta?** Isso apagará permanentemente todos os seus pontos, melhorias e pets salvos!")
    col_sim, col_nao = st.columns(2)
    
    with col_sim:
        if st.button("SIM, deletar tudo", type="primary", use_container_width=True):
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)
            if os.path.exists(LEADERBOARD_FILE):
                os.remove(LEADERBOARD_FILE)
            st.session_state.pontos = 0
            st.session_state.poder_base = 1
            st.session_state.pontos_por_segundo = 0
            st.session_state.pet_slot_1 = None
            st.session_state.pet_slot_2 = None
            st.session_state.ultimo_tick = time.time()
            st.session_state.ja_enviou = False  
            st.session_state.nome_usuario = ""
            st.session_state.confirmando_reset = False
            atualizar_poder_clique()
            st.success("Jogo reiniciado com sucesso!")
            time.sleep(0.5)
            st.rerun()
            
    with col_nao:
        if st.button("NÃO, voltar ao jogo", use_container_width=True):
            st.session_state.confirmando_reset = False
            st.rerun()
