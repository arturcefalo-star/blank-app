import streamlit as st
import time
import random
import json
import os
from streamlit_autorefresh import st_autorefresh

# =====================================================================
# ⚙️ EDITE AQUI OS NOMES E BÔNUS DOS PETS DO MUNDO 2 (LOGOS 7, 8 E 9)
# =====================================================================
NOME_PET_7 = "Barbbie"  # Logo 7
BONUS_PET_7 = 1000000

NOME_PET_8 = "Homem A."     # Logo 8
BONUS_PET_8 = 2500000

NOME_PET_9 = "Tame do cossita"  # Logo 9
BONUS_PET_9 = 5000000

CUSTO_OVO_MUNDO_2_BARATO = 50000000   # Custo do primeiro ovo do Mundo 2

NOME_PET_M2_R1 = "Pocoyo"
BONUS_PET_M2_R1 = 10000000

NOME_PET_M2_R2 = "Bob Construtor"
BONUS_PET_M2_R2 = 25000000

NOME_PET_M2_R3 = "Pintinho A."
BONUS_PET_M2_R3 = 50000000

CUSTO_OVO_MUNDO_2_CARO = 500000000   # Custo do segundo ovo do Mundo 2
# =====================================================================

SENHA_ADMIN = "XxIIlIIxX"
ACCOUNTS_FILE = "usuarios.json"
LEADERBOARD_FILE = "leaderboard.json"

# --- FUNÇÕES DE GERENCIAMENTO DE USUÁRIOS E SALVAMENTO ---

def carregar_todos_usuarios():
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def salvar_todos_usuarios(usuarios):
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=4)

def salvar_progresso_atual():
    if st.session_state.logado and st.session_state.nome_usuario:
        usuarios = carregar_todos_usuarios()
        username_key = st.session_state.nome_usuario.lower()
        
        usuarios[username_key]["dados"] = {
            "pontos": st.session_state.pontos,
            "poder_base": st.session_state.poder_base,
            "pontos_por_segundo": st.session_state.pontos_por_segundo,
            "pet_slot_1": st.session_state.pet_slot_1,
            "pet_slot_2": st.session_state.pet_slot_2,
            "pet_slot_m2_1": st.session_state.pet_slot_m2_1,
            "pet_slot_m2_2": st.session_state.pet_slot_m2_2,
            "ultimo_tick": st.session_state.ultimo_tick,
            "mundo_2_desbloqueado": st.session_state.mundo_2_desbloqueado,
            "mundo_atual": st.session_state.mundo_atual
        }
        salvar_todos_usuarios(usuarios)

def carregar_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                dados = json.load(f)
            return sorted(dados, key=lambda x: x["Pontos"], reverse=True)[:5]
        except Exception:
            return []
    return []

def salvar_leaderboard_completo(lista):
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=4)

def atualizar_no_leaderboard(nome, pontos):
    leaderboard = []
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                leaderboard = json.load(f)
        except Exception:
            pass
    
    encontrado = False
    for j in leaderboard:
        if j["Jogador"].lower() == nome.lower():
            encontrado = True
            if pontos > j["Pontos"]:
                j["Pontos"] = pontos
                j["Jogador"] = nome
            break
    if not encontrado:
        leaderboard.append({"Jogador": nome, "Pontos": pontos})
    
    leaderboard = sorted(leaderboard, key=lambda x: x["Pontos"], reverse=True)[:5]
    salvar_leaderboard_completo(leaderboard)

def remover_jogador_leaderboard(nome):
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                dados = json.load(f)
            novo = [j for j in dados if j["Jogador"].lower() != nome.lower()]
            salvar_leaderboard_completo(novo)
        except Exception:
            pass

# --- INICIALIZAÇÃO DE SESSÃO DO LOGIN ---
if "logado" not in st.session_state:
    st.session_state.logado = False
if "nome_usuario" not in st.session_state:
    st.session_state.nome_usuario = ""

# =====================================================================
# 🔐 TELA DE LOGIN / REGISTRO
# =====================================================================
if not st.session_state.logado:
    st.title("🎮 Clicker Game - Login")
    
    aba_login, aba_registro = st.tabs(["Entrar na Conta", "Criar Nova Conta"])
    
    with aba_login:
        st.subheader("Faça seu Login")
        log_user = st.text_input("Usuário:", key="log_user", max_chars=15).strip()
        log_pass = st.text_input("Senha:", type="password", key="log_pass")
        
        if st.button("Entrar", use_container_width=True):
            usuarios = carregar_todos_usuarios()
            user_key = log_user.lower()
            
            if user_key in usuarios and usuarios[user_key]["senha"] == log_pass:
                # Carrega os dados salvos da conta
                dados = usuarios[user_key]["dados"]
                st.session_state.pontos = dados.get("pontos", 0)
                st.session_state.poder_base = dados.get("poder_base", 1)
                st.session_state.pontos_por_segundo = dados.get("pontos_por_segundo", 0)
                st.session_state.pet_slot_1 = dados.get("pet_slot_1", None)
                st.session_state.pet_slot_2 = dados.get("pet_slot_2", None)
                st.session_state.pet_slot_m2_1 = dados.get("pet_slot_m2_1", None)
                st.session_state.pet_slot_m2_2 = dados.get("pet_slot_m2_2", None)
                st.session_state.ultimo_tick = time.time()  # Evita carregar tempo offline abusivo
                st.session_state.mundo_2_desbloqueado = dados.get("mundo_2_desbloqueado", False)
                st.session_state.mundo_atual = dados.get("mundo_atual", 1)
                
                st.session_state.nome_usuario = usuarios[user_key]["nome_exibicao"]
                st.session_state.logado = True
                st.success(f"Bem-vindo de volta, {st.session_state.nome_usuario}!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
                
    with aba_registro:
        st.subheader("Crie sua Conta")
        reg_user = st.text_input("Escolha um Usuário:", key="reg_user", max_chars=15).strip()
        reg_pass = st.text_input("Escolha uma Senha:", type="password", key="reg_pass")
        reg_pass_conf = st.text_input("Confirme a Senha:", type="password", key="reg_pass_conf")
        
        if st.button("Registrar Conta", use_container_width=True):
            usuarios = carregar_todos_usuarios()
            user_key = reg_user.lower()
            
            if not reg_user or not reg_pass:
                st.warning("Preencha todos os campos!")
            elif user_key in usuarios:
                st.error("Este nome de usuário já existe!")
            elif reg_pass != reg_pass_conf:
                st.error("As senhas não coincidem.")
            else:
                # Registra nova conta com dados iniciais vazios
                usuarios[user_key] = {
                    "senha": reg_pass,
                    "nome_exibicao": reg_user,
                    "dados": {
                        "pontos": 0, "poder_base": 1, "pontos_por_segundo": 0,
                        "pet_slot_1": None, "pet_slot_2": None,
                        "pet_slot_m2_1": None, "pet_slot_m2_2": None,
                        "ultimo_tick": time.time(), "mundo_2_desbloqueado": False, "mundo_atual": 1
                    }
                }
                salvar_todos_usuarios(usuarios)
                st.success("Conta criada com sucesso! Faça login na aba ao lado.")
                
    st.stop() # Interrompe a execução para quem não está logado

# =====================================================================
# 🎮 INTERFACE E LOGICA PRINCIPAL DO JOGO (APÓS LOGAR)
# =====================================================================

if "poder_clique" not in st.session_state:
    st.session_state.poder_clique = 1  
if "ultima_compra" not in st.session_state:
    st.session_state.ultima_compra = 0.0
if "confirmando_reset" not in st.session_state:
    st.session_state.confirmando_reset = False

def atualizar_poder_clique():
    bonus_total = 0
    if st.session_state.pet_slot_1:
        bonus_total += st.session_state.pet_slot_1["bonus"]
    if st.session_state.pet_slot_2:
        bonus_total += st.session_state.pet_slot_2["bonus"]
    if st.session_state.pet_slot_m2_1:
        bonus_total += st.session_state.pet_slot_m2_1["bonus"]
    if st.session_state.pet_slot_m2_2:
        bonus_total += st.session_state.pet_slot_m2_2["bonus"]
    st.session_state.poder_clique = st.session_state.poder_base + bonus_total

atualizar_poder_clique()

# --- REFRESH PASSIVO (AUTO-CLICKER) ---
if st.session_state.pontos_por_segundo > 0:
    st_autorefresh(interval=900, key="autoclicker")

agora = time.time()
tempo_passado = agora - st.session_state.ultimo_tick

if tempo_passado >= 1.0:
    ciclos = int(tempo_passado)
    st.session_state.pontos += st.session_state.pontos_por_segundo * ciclos
    st.session_state.ultimo_tick = agora - (tempo_passado - ciclos)
    salvar_progresso_atual()

loja_em_cooldown = (time.time() - st.session_state.ultima_compra) < 0.5

# --- BARRA LATERAL: PAINEL DO ADMINISTRADOR E LOGOUT ---
with st.sidebar:
    st.write(f"Conectado como: **{st.session_state.nome_usuario}**")
    if st.button("Sair da Conta (Logout)", type="secondary"):
        salvar_progresso_atual()
        st.session_state.logado = False
        st.session_state.nome_usuario = ""
        st.rerun()
        
    st.markdown("---")
    st.header("⚙️ Painel de Admin")
    if st.checkbox("Ativar Modo Administrador"):
        senha_input = st.text_input("Digite a senha de Admin:", type="password")
        
        if len(senha_input) > 0 and senha_input == SENHA_ADMIN:
            st.success("Acesso Permitido!")
            st.subheader("Gerenciar Todos os Usuários")
            
            usuarios_sistema = carregar_todos_usuarios()
            for k, v in list(usuarios_sistema.items()):
                col_adm1, col_adm2 = st.columns([3, 1])
                col_adm1.write(f"👤 {v['nome_exibicao']} ({v['dados']['pontos']:,} pts)")
                if col_adm2.button("Zerar", key=f"zerar_{k}"):
                    v['dados']['pontos'] = 0
                    salvar_todos_usuarios(usuarios_sistema)
                    remover_jogador_leaderboard(v['nome_exibicao'])
                    st.rerun()
        elif senha_input != "":
            st.error("Senha incorreta!")

# --- CONTROLE DE VIAGEM ENTRE MUNDOS ---
st.title("Clicker Game")

CUSTO_MUNDO_2 = 10000000

st.markdown("### Mundos:")
if not st.session_state.mundo_2_desbloqueado:
    desativar_compra_mundo = st.session_state.pontos < CUSTO_MUNDO_2
    if st.button(f"Comprar Mundo 2 (Custo: {CUSTO_MUNDO_2:,} Pts)", disabled=desativar_compra_mundo, use_container_width=True):
        st.session_state.pontos -= CUSTO_MUNDO_2
        st.session_state.mundo_2_desbloqueado = True
        st.session_state.mundo_atual = 2
        salvar_progresso_atual()
        st.success("Indo para o mundo 2...")
        time.sleep(1)
        st.rerun()
else:
    if st.session_state.mundo_atual == 1:
        if st.button("Teleportar para mundo 2", type="primary", use_container_width=True):
            st.session_state.mundo_atual = 2
            salvar_progresso_atual()
            st.rerun()
    else:
        if st.button("Voltar para mundo 1", type="secondary", use_container_width=True):
            st.session_state.mundo_atual = 1
            salvar_progresso_atual()
            st.rerun()

st.markdown("---")

# --- CONTEÚDO DINÂMICO DOS MUNDOS ---
if st.session_state.mundo_atual == 2:
    st.subheader("Segundo mundo")
    st.info("2X de multiplicador de mundo")
    
    if st.button("            Click Here          "):
        st.session_state.pontos += (st.session_state.poder_clique * 2)
        salvar_progresso_atual()

    st.metric(label="Pontos Atuais", value=st.session_state.pontos)
    
    col_status1, col_status2 = st.columns(2)
    col_status1.write(f"**Poder de clique:** {st.session_state.poder_clique * 2} (2X)")
    col_status2.write(f"**Pontos por segundo:** {st.session_state.pontos_por_segundo}")

    st.markdown("---")
    st.subheader("Comprar ovos:")
    col_m2_egg1, col_m2_egg2 = st.columns(2)

    with col_m2_egg1:
        st.write("### Ovo Épico:")
        st.write(f"{NOME_PET_7}: 50% (+{BONUS_PET_7:,} Pts)")
        st.write(f"{NOME_PET_8}: 35% (+{BONUS_PET_8:,} Pts)")
        st.write(f"{NOME_PET_9}: 15% (+{BONUS_PET_9:,} Pts)")
        
        desativar_m2_ovo1 = st.session_state.pontos < CUSTO_OVO_MUNDO_2_BARATO or loja_em_cooldown
        
        if st.button(f"Abrir Ovo = {CUSTO_OVO_MUNDO_2_BARATO:,} Pontos", disabled=desativar_m2_ovo1, key="botao_m2_ovo1"):
            st.session_state.ultima_compra = time.time()  
            if st.session_state.pontos >= CUSTO_OVO_MUNDO_2_BARATO:
                st.session_state.pontos -= CUSTO_OVO_MUNDO_2_BARATO
                sorteado = random.choices(
                   [{"nome": NOME_PET_7, "arquivo": "logo7.png", "bonus": BONUS_PET_7, "chance": "50%"}, 
                    {"nome": NOME_PET_8, "arquivo": "logo8.png", "bonus": BONUS_PET_8, "chance": "35%"},
                    {"nome": NOME_PET_9, "arquivo": "logo9.png", "bonus": BONUS_PET_9, "chance": "15%"}],
                   weights=[50, 35, 15], k=1
                )[0]
                st.session_state.pet_slot_m2_1 = sorteado
                atualizar_poder_clique()
                salvar_progresso_atual()
                time.sleep(0.5) 
                st.rerun()

        if st.session_state.pet_slot_m2_1:
            pet = st.session_state.pet_slot_m2_1
            st.write("**Pet Equipado:**")
            st.caption(f"{pet['nome']} ({pet['chance']}) | +{pet['bonus']:,} por clique")

    with col_m2_egg2:
        st.write("### Ovo Lendádio:")
        st.write(f"{NOME_PET_M2_R1}: 50% (+{BONUS_PET_M2_R1:,} Pts)")
        st.write(f"{NOME_PET_M2_R2}: 35% (+{BONUS_PET_M2_R2:,} Pts)")
        st.write(f"{NOME_PET_M2_R3}: 15% (+{BONUS_PET_M2_R3:,} Pts)")
        
        desativar_m2_ovo2 = st.session_state.pontos < CUSTO_OVO_MUNDO_2_CARO or loja_em_cooldown
        
        if st.button(f"Abrir Ovo = {CUSTO_OVO_MUNDO_2_CARO:,} Pontos", disabled=desativar_m2_ovo2, key="botao_m2_ovo2"):
            st.session_state.ultima_compra = time.time()
            if st.session_state.pontos >= CUSTO_OVO_MUNDO_2_CARO:
                st.session_state.pontos -= CUSTO_OVO_MUNDO_2_CARO
                sorteado = random.choices(
                   [{"nome": NOME_PET_M2_R1, "arquivo": "logo10.png", "bonus": BONUS_PET_M2_R1, "chance": "50%"}, 
                    {"nome": NOME_PET_M2_R2, "arquivo": "logo11.png", "bonus": BONUS_PET_M2_R2, "chance": "35%"},
                    {"nome": NOME_PET_M2_R3, "arquivo": "logo12.png", "bonus": BONUS_PET_M2_R3, "chance": "15%"}],
                   weights=[50, 35, 15], k=1
                )[0]
                st.session_state.pet_slot_m2_2 = sorteado
                atualizar_poder_clique()
                salvar_progresso_atual()
                time.sleep(0.5) 
                st.rerun()

        if st.session_state.pet_slot_m2_2:
            pet = st.session_state.pet_slot_m2_2
            st.write("**Pet Equipado:**")
            st.caption(f"{pet['nome']} ({pet['chance']}) | +{pet['bonus']:,} por clique")

else:
    st.subheader("Primeiro Mundo")
    
    if st.button("            Click Here          "):
        st.session_state.pontos += st.session_state.poder_clique
        salvar_progresso_atual()

    st.metric(label="Pontos Atuais", value=st.session_state.pontos)
    col_status1, col_status2 = st.columns(2)
    col_status1.write(f"**Poder de clique:** {st.session_state.poder_clique}")
    col_status2.write(f"**Pontos por segundo:** {st.session_state.pontos_por_segundo}")

    st.markdown("---")
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
                salvar_progresso_atual()
                time.sleep(0.5) 
                st.rerun()

        if st.session_state.pet_slot_1:
            pet = st.session_state.pet_slot_1
            st.write("**Pet Equipado:**")
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
                salvar_progresso_atual()
                time.sleep(0.5) 
                st.rerun()

        if st.session_state.pet_slot_2:
            pet = st.session_state.pet_slot_2
            st.write("**Pet Equipado:**")
            st.caption(f"{pet['nome']} ({pet['chance']}) | +{pet['bonus']} por clique")

st.markdown("---")

# --- LOJA DE MELHORIAS ---
st.subheader("Loja de Melhorias")

if st.session_state.mundo_atual == 2:
    melhorias_clique = [
        {"qtd": 50000, "custo": 15000000}, {"qtd": 100000, "custo": 50000000},
        {"qtd": 250000, "custo": 150000000}, {"qtd": 500000, "custo": 500000000},
        {"qtd": 1000000, "custo": 1000000000}, {"qtd": 2500000, "custo": 3500000000},
        {"qtd": 5000000, "custo": 8000000000}, {"qtd": 10000000, "custo": 20000000000},
        {"qtd": 25000000, "custo": 50000000000}, {"qtd": 50000000, "custo": 100000000000}
    ]
    melhorias_passivas = [
        {"qtd": 50000, "custo": 4000000}, {"qtd": 100000, "custo": 12000000},
        {"qtd": 250000, "custo": 40000000}, {"qtd": 500000, "custo": 120000000},
        {"qtd": 1000000, "custo": 400000000}, {"qtd": 2000000, "custo": 1000000000},
        {"qtd": 5000000, "custo": 3000000000}, {"qtd": 10000000, "custo": 7500000000},
        {"qtd": 20000000, "custo": 15000000000}, {"qtd": 50000000, "custo": 40000000000}
    ]
else:
    melhorias_clique = [
        {"qtd": 1, "custo": 100}, {"qtd": 5, "custo": 500}, {"qtd": 10, "custo": 1000},
        {"qtd": 50, "custo": 5000}, {"qtd": 100, "custo": 10000}, {"qtd": 500, "custo": 50000},
        {"qtd": 1000, "custo": 100000}, {"qtd": 2500, "custo": 250000}, {"qtd": 5000, "custo": 500000},
        {"qtd": 10000, "custo": 1000000}
    ]
    melhorias_passivas = [
        {"qtd": 5, "custo": 200}, {"qtd": 10, "custo": 600}, {"qtd": 20, "custo": 1100},
        {"qtd": 100, "custo": 7500}, {"qtd": 200, "custo": 14500}, {"qtd": 1000, "custo": 72500},
        {"qtd": 2000, "custo": 145000}, {"qtd": 5000, "custo": 360000}, {"qtd": 10000, "custo": 725000},
        {"qtd": 20000, "custo": 1450000}
    ]

col1, col2 = st.columns(2)

with col1:
    st.subheader("Melhoria Clicker")
    with st.container(height=350):
        for i, item in enumerate(melhorias_clique):
            texto = f"+{item['qtd']:,} clk | {item['custo']:,} Pts"
            desativado = st.session_state.pontos < item['custo'] or loja_em_cooldown
            key_btn = f"c_{st.session_state.mundo_atual}_{i}"

            if st.button(texto, key=key_btn, disabled=desativado, use_container_width=True):
                st.session_state.ultima_compra = time.time()
                st.session_state.pontos -= item['custo']
                st.session_state.poder_base += item['qtd']
                atualizar_poder_clique()  
                salvar_progresso_atual()
                time.sleep(0.5)
                st.rerun()

with col2:
    st.subheader("Auto Clickers")
    with st.container(height=350):
        for i, item in enumerate(melhorias_passivas):
            texto = f"+{item['qtd']:,}/s | {item['custo']:,} Pts"
            desativado = st.session_state.pontos < item['custo'] or loja_em_cooldown
            key_btn = f"p_{st.session_state.mundo_atual}_{i}"

            if st.button(texto, key=key_btn, disabled=desativado, use_container_width=True):
                st.session_state.ultima_compra = time.time()
                st.session_state.pontos -= item['custo']
                st.session_state.pontos_por_segundo += item['qtd']
                salvar_progresso_atual()
                time.sleep(0.5)
                st.rerun()

# --- ATUALIZAÇÕES AUTOMÁTICAS NO LEADERBOARD ---
atualizar_no_leaderboard(st.session_state.nome_usuario, st.session_state.pontos)

# --- TABELA DE CLASSIFICAÇÃO GLOBAL ---
st.markdown("---")
st.subheader("🏆 Top 5 Global:")
dados_placar = carregar_leaderboard()

if dados_placar:
    st.table(dados_placar)
else:
    st.info("O placar está vazio.")

# --- LOG DE ATUALIZAÇÕES ---
st.markdown("---")
st.subheader("Log de Atualizações:")
st.write("(1.9.0) - Adicionado Sistema de Login e Registro seguro por senha!")
st.write("(1.8.9) - Adição de 2 novos ovos (segundo mundo), 6 novos pets e correções.")

# --- SISTEMA DE RESET DE JOGO ---
st.markdown("---")
if not st.session_state.confirmando_reset:
    if st.button("Resetar Minha Conta", use_container_width=True):
        st.session_state.confirmando_reset = True
        st.rerun()
else:
    st.warning("⚠️ **Você tem certeza?** Isso apagará seu progresso atual e te removerá do Placar!")
    col_sim, col_nao = st.columns(2)
    
    with col_sim:
        if st.button("SIM, deletar tudo", type="primary", use_container_width=True):
            remover_jogador_leaderboard(st.session_state.nome_usuario)
            
            # Limpa o progresso no arquivo global de usuários
            usuarios = carregar_todos_usuarios()
            user_key = st.session_state.nome_usuario.lower()
            if user_key in usuarios:
                usuarios[user_key]["dados"] = {
                    "pontos": 0, "poder_base": 1, "pontos_por_segundo": 0,
                    "pet_slot_1": None, "pet_slot_2": None,
                    "pet_slot_m2_1": None, "pet_slot_m2_2": None,
                    "ultimo_tick": time.time(), "mundo_2_desbloqueado": False, "mundo_atual": 1
                }
                salvar_todos_usuarios(usuarios)
                
            st.session_state.logado = False
            st.session_state.nome_usuario = ""
            st.success("Jogo reiniciado com sucesso! Reconecte.")
            time.sleep(1)
            st.rerun()
            
    with col_nao:
        if st.button("NÃO, voltar ao jogo", use_container_width=True):
            st.session_state.confirmando_reset = False
            st.rerun()
