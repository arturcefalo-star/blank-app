import streamlit as st
import time
import random
import json
import os
from streamlit_autorefresh import st_autorefresh

# =====================================================================
# ⚙️ EDITE AQUI OS NOMES E BÔNUS BASE DOS PETS DO MUNDO 2 (LOGOS 7, 8 E 9)
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

SENHA_ADMIN = "XXxx67xxXX"
SENHA_ADMIN2 = "lililili"
ACCOUNTS_FILE = "usuarios.json"
LEADERBOARD_FILE = "leaderboard.json"
AVISOS_FILE = "avisos.json"
SESSION_FILE = "sessao_ativa.json"  # Arquivo que lembra quem está logado

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
        
        if username_key in usuarios:
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
            atualizar_no_leaderboard(st.session_state.nome_usuario, st.session_state.pontos)

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
            j["Pontos"] = pontos  
            j["Jogador"] = nome
            break
            
    if not encontrado:
        leaderboard.append({"Jogador": nome, "Pontos": pontos})
    
    leaderboard = sorted(leaderboard, key=lambda x: x["Pontos"], reverse=True)
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

def carregar_configuracoes_globais():
    if os.path.exists(AVISOS_FILE):
        try:
            with open(AVISOS_FILE, "r", encoding="utf-8") as f:
                dados = json.load(f)
                if "multiplicador_evento" not in dados:
                    dados["multiplicador_evento"] = 1
                if "multiplicador_sorte" not in dados:
                    dados["multiplicador_sorte"] = 1
                return dados
        except Exception:
            return {"mensagem": "", "multiplicador_evento": 1, "multiplicador_sorte": 1}
    return {"mensagem": "", "multiplicador_evento": 1, "multiplicador_sorte": 1}

def salvar_configuracoes_globais(dados):
    with open(AVISOS_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# --- FUNÇÕES DE AUTO-LOGIN (PERSISTÊNCIA DE SESSÃO) ---
def salvar_sessao_ativa(username):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump({"usuario_ativo": username}, f)

def limpar_sessao_ativa():
    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
        except Exception:
            pass

def verificar_auto_login():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                dados_sessao = json.load(f)
                return dados_sessao.get("usuario_ativo", "").lower()
        except Exception:
            return None
    return None


# --- INICIALIZAÇÃO DE SESSÃO DO LOGIN ---
if "logado" not in st.session_state:
    st.session_state.logado = False
if "nome_usuario" not in st.session_state:
    st.session_state.nome_usuario = ""

# --- CHECAGEM AUTOMÁTICA DE LOGIN ---
if not st.session_state.logado:
    usuario_salvo = verificar_auto_login()
    if usuario_salvo:
        usuarios = carregar_todos_usuarios()
        if usuario_salvo in usuarios:
            dados = usuarios[usuario_salvo]["dados"]
            st.session_state.pontos = dados.get("pontos", 0)
            st.session_state.poder_base = dados.get("poder_base", 1)
            st.session_state.pontos_por_segundo = dados.get("pontos_por_segundo", 0)
            st.session_state.pet_slot_1 = dados.get("pet_slot_1", None)
            st.session_state.pet_slot_2 = dados.get("pet_slot_2", None)
            st.session_state.pet_slot_m2_1 = dados.get("pet_slot_m2_1", None)
            st.session_state.pet_slot_m2_2 = dados.get("pet_slot_m2_2", None)
            st.session_state.ultimo_tick = dados.get("ultimo_tick", time.time())
            st.session_state.mundo_2_desbloqueado = dados.get("mundo_2_desbloqueado", False)
            st.session_state.mundo_atual = dados.get("mundo_atual", 1)
            st.session_state.pontos_leaderboard_cache = dados.get("pontos", 0)
            st.session_state.nome_usuario = usuarios[usuario_salvo]["nome_exibicao"]
            st.session_state.logado = True

# =====================================================================
# 🔐 TELA DE LOGIN / REGISTRO
# =====================================================================
if not st.session_state.logado:
    st.title("Clicker Game - Login")
    
    aba_login, aba_registro = st.tabs(["Entrar na Conta", "Criar Nova Conta"])
    
    with aba_login:
        st.subheader("Faça seu Login")
        log_user = st.text_input("Usuário:", key="log_user", max_chars=15).strip()
        log_pass = st.text_input("Senha:", type="password", key="log_pass")
        
        if st.button("Entrar", use_container_width=True):
            usuarios = carregar_todos_usuarios()
            user_key = log_user.lower()
            
            if user_key in usuarios and usuarios[user_key]["senha"] == log_pass:
                dados = usuarios[user_key]["dados"]
                st.session_state.pontos = dados.get("pontos", 0)
                st.session_state.poder_base = dados.get("poder_base", 1)
                st.session_state.pontos_por_segundo = dados.get("pontos_por_segundo", 0)
                st.session_state.pet_slot_1 = dados.get("pet_slot_1", None)
                st.session_state.pet_slot_2 = dados.get("pet_slot_2", None)
                st.session_state.pet_slot_m2_1 = dados.get("pet_slot_m2_1", None)
                st.session_state.pet_slot_m2_2 = dados.get("pet_slot_m2_2", None)
                st.session_state.ultimo_tick = dados.get("ultimo_tick", time.time())
                st.session_state.mundo_2_desbloqueado = dados.get("mundo_2_desbloqueado", False)
                st.session_state.mundo_atual = dados.get("mundo_atual", 1)
                st.session_state.pontos_leaderboard_cache = dados.get("pontos", 0)
                
                st.session_state.nome_usuario = usuarios[user_key]["nome_exibicao"]
                st.session_state.logado = True
                
                salvar_sessao_ativa(user_key)
                
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
                
    st.stop()

# =====================================================================
# 🎮 INTERFACE E LOGICA PRINCIPAL DO JOGO (APÓS LOGAR)
# =====================================================================

if "poder_clique" not in st.session_state:
    st.session_state.poder_clique = 1  
if "ultima_compra" not in st.session_state:
    st.session_state.ultima_compra = 0.0
if "confirmando_reset" not in st.session_state:
    st.session_state.confirmando_reset = False
if "pontos_leaderboard_cache" not in st.session_state:
    st.session_state.pontos_leaderboard_cache = st.session_state.pontos
if "ultimo_tick" not in st.session_state:
    st.session_state.ultimo_tick = time.time()

config_globais = carregar_configuracoes_globais()
aviso_sistema = config_globais.get("mensagem", "")
mult_evento = config_globais.get("multiplicador_evento", 1) 
mult_sorte = config_globais.get("multiplicador_sorte", 1)

def calcular_bonus_pet(pet):
    if not pet:
        return 0
    return pet["bonus"]

def atualizar_poder_clique():
    bonus_total = 0
    bonus_total += calcular_bonus_pet(st.session_state.pet_slot_1)
    bonus_total += calcular_bonus_pet(st.session_state.pet_slot_2)
    bonus_total += calcular_bonus_pet(st.session_state.pet_slot_m2_1)
    bonus_total += calcular_bonus_pet(st.session_state.pet_slot_m2_2)
    
    poder_calculado = st.session_state.poder_base + bonus_total
    st.session_state.poder_clique = poder_calculado * mult_evento

def calcular_chances_ovo(c1, c2, c3_base):
    c3_atual = min(c3_base * mult_sorte, 90)
    restante = 100 - c3_atual
    soma_base_comuns = c1 + c2
    
    c1_atual = (c1 / soma_base_comuns) * restante
    c2_atual = (c2 / soma_base_comuns) * restante
    return c1_atual, c2_atual, c3_atual

atualizar_poder_clique()

# --- 🚀 SISTEMA ANTI-LAG DEFINITIVO COM FRAGMENTO OTIMIZADO ---
@st.fragment
def renderizar_area_clique():
    st_autorefresh(interval=3000, key="game_click_loop")
    
    agora = time.time()
    tempo_passado = agora - st.session_state.ultimo_tick

    if tempo_passado >= 1.0:
        ciclos = int(tempo_passado)
        st.session_state.pontos += st.session_state.pontos_por_segundo * ciclos
        st.session_state.ultimo_tick = agora - (tempo_passado - ciclos)
        st.session_state.pontos_leaderboard_cache = st.session_state.pontos
        salvar_progresso_atual()

    st.metric(label="Pontos Atuais", value=st.session_state.pontos)
    
    if st.session_state.mundo_atual == 2:
        if st.button("            Click Here          ", key="click_m2_btn", use_container_width=True):
            st.session_state.pontos += (st.session_state.poder_clique * 2)
            st.session_state.pontos_leaderboard_cache = st.session_state.pontos
            salvar_progresso_atual()
        st.write(f"**Poder de clique:** {st.session_state.poder_clique * 2} (2X do Mundo)")
    else:
        if st.button("            Click Here          ", key="click_m1_btn", use_container_width=True):
            st.session_state.pontos += st.session_state.poder_clique
            st.session_state.pontos_leaderboard_cache = st.session_state.pontos
            salvar_progresso_atual()
        st.write(f"**Poder de clique:** {st.session_state.poder_clique}")
        
    st.write(f"**Pontos por segundo:** {st.session_state.pontos_por_segundo}")


# Sincronização em background segura do placar
if st.session_state.nome_usuario != "" and os.path.exists(LEADERBOARD_FILE):
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            tabela_global = json.load(f)
        for j in tabela_global:
            if j["Jogador"].lower() == st.session_state.nome_usuario.lower():
                pontos_lb = j.get("Points", j.get("Pontos", 0))
                if pontos_lb != st.session_state.pontos_leaderboard_cache:
                    st.session_state.pontos = pontos_lb
                    st.session_state.pontos_leaderboard_cache = pontos_lb
                break
    except Exception:
        pass

loja_em_cooldown = (time.time() - st.session_state.ultima_compra) < 0.6

# --- BARRA LATERAL: LOGOUT, PAINEL ADMIN E TRAPAÇAS ---
with st.sidebar:
    st.write(f"Conectado como: **{st.session_state.nome_usuario}**")
    if st.button("Sair da Conta (Logout)", type="secondary"):
        salvar_progresso_atual()
        limpar_sessao_ativa()  
        st.session_state.logado = False
        st.session_state.nome_usuario = ""
        st.rerun()
        
    st.markdown("---")
    st.header("⚙️ Painel de Admin")
    if st.checkbox("Ativar Modo Administrador"):
        senha_input = st.text_input("Digite a senha de Admin:", type="password", key="pwd_admin")
        
        if len(senha_input) > 0 and senha_input == SENHA_ADMIN:
            st.success("Success!")
            
            st.subheader("Gerenciar Placar Global")
            
            placar_completo = []
            if os.path.exists(LEADERBOARD_FILE):
                try:
                    with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                        placar_completo = json.load(f)
                except Exception:
                    pass

            if placar_completo:
                for jogador in placar_completo:
                    st.write(f" **{jogador['Jogador']}**: {jogador['Pontos']} pts")
            else:
                st.info("Nenhum jogador registrado no placar ainda.")
                
            st.markdown("---")
            st.subheader("Mensagem Global")
            nova_msg = st.text_input("Texto Global:", value=aviso_sistema, placeholder="Digite o aviso geral aqui...")
            
            col_msg1, col_msg2 = st.columns(2)
            if col_msg1.button("Enviar Mensagem", use_container_width=True):
                config_globais["mensagem"] = nova_msg
                salvar_configuracoes_globais(config_globais)
                st.success("Mensagem enviada!")
                time.sleep(0.3)
                st.rerun()
                
            if col_msg2.button("Apagar", type="secondary", use_container_width=True):
                config_globais["mensagem"] = ""
                salvar_configuracoes_globais(config_globais)
                st.rerun()

            st.markdown("---")
            st.subheader("Inspecionar Jogador")

            usuarios_db_inspect = carregar_todos_usuarios()
            lista_jogadores = [usuarios_db_inspect[k]["nome_exibicao"] for k in usuarios_db_inspect]

            if lista_jogadores:
                jogador_selecionado = st.selectbox("Selecione um jogador:", lista_jogadores, key="inspect_select")
                
                if "jogador_sob_inspecao" not in st.session_state:
                    st.session_state.jogador_sob_inspecao = None

                if st.button("Inspecionar Dados", use_container_width=True):
                    st.session_state.jogador_sob_inspecao = jogador_selecionado

                if st.session_state.jogador_sob_inspecao:
                    alvo_atual = st.session_state.inspect_select
                    key_inspect = alvo_atual.lower()
                    dados_player = usuarios_db_inspect[key_inspect]["dados"]
                    
                    st.markdown(f"### Status de: **{alvo_atual}**")
                    
                    col_ins1, col_ins2, col_ins3 = st.columns(3)
                    col_ins1.metric("Pontos", f"{dados_player.get('pontos', 0):,}")
                    col_ins2.metric("Poder Base", f"{dados_player.get('poder_base', 1):,}")
                    col_ins3.metric("Pontos/Seg", f"{dados_player.get('pontos_por_segundo', 0):,}")
                    
                    mundo_txt = "Mundo 2" if dados_player.get("mundo_atual", 1) == 2 else "Mundo 1"
                    m2_liberado = "Sim" if dados_player.get("mundo_2_desbloqueado", False) else "Não"
                    st.write(f" **Mundo Atual:** {mundo_txt} | **Mundo 2 Desbloqueado?** {m2_liberado}")
                    
                    st.markdown(" **Pets Equipados:**")
                    col_p1, col_p2 = st.columns(2)
                    
                    with col_p1:
                        st.write("**Mundo 1 Slots:**")
                        p1 = dados_player.get("pet_slot_1")
                        p2 = dados_player.get("pet_slot_2")
                        st.write(f"Slot 1: {p1['nome']} (+{p1['bonus']:,})" if p1 else "Slot 1: Vazio")
                        st.write(f"Slot 2: {p2['nome']} (+{p2['bonus']:,})" if p2 else "Slot 2: Vazio")
                        
                    with col_p2:
                        st.write("**Mundo 2 Slots:**")
                        pm1 = dados_player.get("pet_slot_m2_1")
                        pm2 = dados_player.get("pet_slot_m2_2")
                        st.write(f"Slot 1: {pm1['nome']} (+{pm1['bonus']:,})" if pm1 else "Slot 3: Vazio")
                        st.write(f"Slot 2: {pm2['nome']} (+{pm2['bonus']:,})" if pm2 else "Slot 4: Vazio")

                    st.markdown("---")
                    qtd_pontos = st.number_input("Quantidade de pontos (Add/Rem):", min_value=1, value=1000, step=100, key="qtd_pontos_adm")

                    st.markdown(" **Ações Disponíveis:**")
                    col_adm1, col_adm2, col_adm3 = st.columns(3)
                    
                    if col_adm1.button("Ban", key=f"del_{key_inspect}", use_container_width=True):
                        if key_inspect in usuarios_db_inspect:
                            usuarios_db_inspect[key_inspect]["dados"] = {
                                "pontos": 0, "poder_base": 1, "pontos_por_segundo": 0,
                                "pet_slot_1": None, "pet_slot_2": None,
                                "pet_slot_m2_1": None, "pet_slot_m2_2": None,
                                "ultimo_tick": time.time(), "mundo_2_desbloqueado": False, "mundo_atual": 1
                            }
                            salvar_todos_usuarios(usuarios_db_inspect)
                        
                        for j in placar_completo:
                            if j["Jogador"].lower() == key_inspect:
                                j["Points"] = 0
                                if "Pontos" in j: j["Pontos"] = 0
                                break
                        salvar_leaderboard_completo(placar_completo)

                        if key_inspect == st.session_state.nome_usuario.lower():
                            st.session_state.pontos = 0
                            st.session_state.poder_base = 1
                            st.session_state.pontos_por_segundo = 0
                            st.session_state.pet_slot_1 = None
                            st.session_state.pet_slot_2 = None
                            st.session_state.pet_slot_m2_1 = None
                            st.session_state.pet_slot_m2_2 = None
                            st.session_state.mundo_2_desbloqueado = False
                            st.session_state.mundo_atual = 1
                            st.session_state.pontos_leaderboard_cache = 0
                            atualizar_poder_clique()
                        st.rerun()
                    
                    if col_adm2.button("Add", key=f"add_{key_inspect}", use_container_width=True):
                        if key_inspect in usuarios_db_inspect:
                            usuarios_db_inspect[key_inspect]["dados"]["pontos"] = max(0, usuarios_db_inspect[key_inspect]["dados"].get("pontos", 0) + qtd_pontos)
                            salvar_todos_usuarios(usuarios_db_inspect)
                            
                        if key_inspect == st.session_state.nome_usuario.lower():
                            st.session_state.pontos += qtd_pontos
                            st.session_state.pontos_leaderboard_cache = st.session_state.pontos
                            
                        for j in placar_completo:
                            if j["Jogador"].lower() == key_inspect:
                                if "Pontos" in j: j["Pontos"] += qtd_pontos
                                if "Points" in j: j["Points"] += qtd_pontos
                                break
                        salvar_leaderboard_completo(placar_completo)
                        st.rerun()

                    if col_adm3.button("Rem", key=f"rem_{key_inspect}", use_container_width=True):
                        if key_inspect in usuarios_db_inspect:
                            usuarios_db_inspect[key_inspect]["dados"]["pontos"] = max(0, usuarios_db_inspect[key_inspect]["dados"].get("pontos", 0) - qtd_pontos)
                            salvar_todos_usuarios(usuarios_db_inspect)
                            
                        if key_inspect == st.session_state.nome_usuario.lower():
                            st.session_state.pontos = max(0, st.session_state.pontos - qtd_pontos)
                            st.session_state.pontos_leaderboard_cache = st.session_state.pontos
                            
                        for j in placar_completo:
                            if j["Jogador"].lower() == key_inspect:
                                if "Pontos" in j: j["Pontos"] = max(0, j["Pontos"] - qtd_pontos)
                                if "Points" in j: j["Points"] = max(0, j["Points"] - qtd_pontos)
                                break
                        salvar_leaderboard_completo(placar_completo)
                        st.rerun()
            else:
                st.info("Nenhum jogador cadastrado para inspecionar.")
                
            st.markdown("---")
            st.subheader("Eventos de adimin")
            
            status_evento = f"ATIVADO ({mult_evento}X)" if mult_evento > 1 else "DESATIVADO"
            st.write(f"Multiplicador de Dinheiro: **{status_evento}**")
            
            col_ev2x, col_ev3x, col_ev4x, col_ev5x = st.columns(4)
            if col_ev2x.button("Ativar 2X", key="btn_ev2", use_container_width=True, disabled=(mult_evento == 2)):
                config_globais["multiplicador_evento"] = 2
                salvar_configuracoes_globais(config_globais)
                st.success("Evento 2X Ativado!")
                time.sleep(0.4)
                st.rerun()
            if col_ev3x.button("Ativar 3X", key="btn_ev3", use_container_width=True, disabled=(mult_evento == 3)):
                config_globais["multiplicador_evento"] = 3
                salvar_configuracoes_globais(config_globais)
                st.success("Evento 3X Ativado!")
                time.sleep(0.4)
                st.rerun()
            if col_ev4x.button("Ativar 4X", key="btn_ev4", use_container_width=True, disabled=(mult_evento == 4)):
                config_globais["multiplicador_evento"] = 4
                salvar_configuracoes_globais(config_globais)
                st.success("Evento 4X Ativado!")
                time.sleep(0.4)
                st.rerun()
            if col_ev5x.button("Ativar 5X", key="btn_ev5", use_container_width=True, disabled=(mult_evento == 5)):
                config_globais["multiplicador_evento"] = 5
                salvar_configuracoes_globais(config_globais)
                st.success("Evento 5X Ativado!")
                time.sleep(0.4)
                st.rerun()
            
            if st.button("Desativar", type="secondary", use_container_width=True, disabled=(mult_evento == 1), key="btn_desativar_evento"):
                config_globais["multiplicador_evento"] = 1
                salvar_configuracoes_globais(config_globais)
                st.warning("Multiplicador do Evento Disativado!")
                time.sleep(0.4)
                st.rerun()

            status_sorte = f"ATIVADO ({mult_sorte}X)" if mult_sorte > 1 else "DESATIVADO"
            st.write(f"Multiplicador de Sorte: **{status_sorte}**")

            col_st2x, col_st3x, col_st4x, col_st5x = st.columns(4)
            if col_st2x.button("Sorte 2X", key="btn_st2", use_container_width=True, disabled=(mult_sorte == 2)):
                config_globais["multiplicador_sorte"] = 2
                salvar_configuracoes_globais(config_globais)
                st.success("Sorte de Drop 2X Ativada!")
                time.sleep(0.4)
                st.rerun()
            if col_st3x.button("Sorte 3X", key="btn_st3", use_container_width=True, disabled=(mult_sorte == 3)):
                config_globais["multiplicador_sorte"] = 3
                salvar_configuracoes_globais(config_globais)
                st.success("Sorte de Drop 3X Ativada!")
                time.sleep(0.4)
                st.rerun()
            if col_st4x.button("Sorte 4X", key="btn_st4", use_container_width=True, disabled=(mult_sorte == 4)):
                config_globais["multiplicador_sorte"] = 4
                salvar_configuracoes_globais(config_globais)
                st.success("Sorte de Drop 4X Ativada!")
                time.sleep(0.4)
                st.rerun()
            if col_st5x.button("Sorte 5X", key="btn_st5", use_container_width=True, disabled=(mult_sorte == 5)):
                config_globais["multiplicador_sorte"] = 5
                salvar_configuracoes_globais(config_globais)
                st.success("Sorte de Drop 5X Ativada!")
                time.sleep(0.4)
                st.rerun()

            if st.button("Desativar", type="secondary", use_container_width=True, disabled=(mult_sorte == 1), key="btn_desativar_sorte"):
                config_globais["multiplicador_sorte"] = 1
                salvar_configuracoes_globais(config_globais)
                st.warning("Multiplicador de Sorte Desativado!")
                time.sleep(0.4)
                st.rerun()
                
        elif senha_input != "":
            st.error("Senha incorreta!")

    # =====================================================================
    # ✨ MENU DE TRAPAÇAS (FUNÇÕES BÁSICAS PARA SI MESMO)
    # =====================================================================
    st.markdown("---")
    st.header("⚙️ Ativar modo Apoiador")
    if st.checkbox("Ativar Modo Apoiador"):
        senha_cheat = st.text_input("Digite a senha de Apoiador:", type="password", key="pwd_cheat")
        
        if len(senha_cheat) > 0 and senha_cheat == SENHA_ADMIN2:
            st.success("Success! ")
            
            qtd_cheat = st.number_input("Quantidade de Pontos:", min_value=1, value=5000, step=500, key="qtd_cheat_val")
            
            col_ch1, col_ch2 = st.columns(2)
            
            if col_ch1.button("Add", use_container_width=True):
                st.session_state.pontos += qtd_cheat
                st.session_state.pontos_leaderboard_cache = st.session_state.pontos
                salvar_progresso_atual()
                st.success(f"+{qtd_cheat:,} pontos adicionados!")
                time.sleep(0.4)
                st.rerun()
                
            if col_ch2.button("Rem", use_container_width=True):
                st.session_state.pontos = max(0, st.session_state.pontos - qtd_cheat)
                st.session_state.pontos_leaderboard_cache = st.session_state.pontos
                salvar_progresso_atual()
                st.warning(f"{qtd_cheat:,} pontos removidos!")
                time.sleep(0.4)
                st.rerun()
                
        elif senha_cheat != "":
            st.error("Senha incorreta!")

# --- CONTROLE DE VIAGEM ENTRE MUNDOS ---
st.title("Clicker Game")

if aviso_sistema.strip() != "":
    st.info(f" **Mensagem do ADM:** {aviso_sistema}")

if mult_evento > 1:
    st.warning(f" **EVENTO GLOBAL ATIVO:** Cliques concedendo o **{mult_evento}X** de Pontos em todos os mundos!")

if mult_sorte > 1:
    st.success(f" **EVENTO DE SORTE ATIVO:** Chances de ganhar Pets Raros **{mult_sorte}X**!")

CUSTO_MUNDO_2 = 10000000

st.markdown("### Mundos:")
if not st.session_state.mundo_2_desbloqueado:
    desativar_compra_mundo = st.session_state.pontos < CUSTO_MUNDO_2
    if st.button(f"Comprar Mundo 2 (Custo: {CUSTO_MUNDO_2:,} Pts)", disabled=desativar_compra_mundo, use_container_width=True):
        if st.session_state.pontos >= CUSTO_MUNDO_2:
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
    
    st.write("Trilha sonora: on/off")
    try:
        st.audio("musica67.mp3") 
    except Exception:
        pass

    renderizar_area_clique()

    st.markdown("---")
    st.subheader("Comprar ovos:")
    col_m2_egg1, col_m2_egg2 = st.columns(2)

    ch1_m2_o1, ch2_m2_o1, ch3_m2_o1 = calcular_chances_ovo(50, 35, 15)

    with col_m2_egg1:
        st.write("### Ovo Épico:")
        st.write(f"{NOME_PET_7}: {ch1_m2_o1:.1f}% (+{BONUS_PET_7:,} Pts)")
        st.write(f"{NOME_PET_8}: {ch2_m2_o1:.1f}% (+{BONUS_PET_8:,} Pts)")
        st.write(f"{NOME_PET_9}: **{ch3_m2_o1:.1f}%** (+{BONUS_PET_9:,} Pts)")
        
        desativar_m2_ovo1 = st.session_state.pontos < CUSTO_OVO_MUNDO_2_BARATO or loja_em_cooldown
        
        if st.button(f"Abrir Ovo = {CUSTO_OVO_MUNDO_2_BARATO:,} Pontos", disabled=desativar_m2_ovo1, key="botao_m2_ovo1"):
            st.session_state.ultima_compra = time.time()  
            if st.session_state.pontos >= CUSTO_OVO_MUNDO_2_BARATO:
                st.session_state.pontos -= CUSTO_OVO_MUNDO_2_BARATO
                sorteado = random.choices(
                   [{"nome": NOME_PET_7, "arquivo": "logo7.png", "bonus": BONUS_PET_7, "chance": "50%"}, 
                    {"nome": NOME_PET_8, "arquivo": "logo8.png", "bonus": BONUS_PET_8, "chance": "35%"},
                    {"nome": NOME_PET_9, "arquivo": "logo9.png", "bonus": BONUS_PET_9, "chance": "15%"}],
                   weights=[ch1_m2_o1, ch2_m2_o1, ch3_m2_o1], k=1
                )[0]
                st.session_state.pet_slot_m2_1 = sorteado
                atualizar_poder_clique()
                salvar_progresso_atual()
                time.sleep(0.5) 
                st.rerun()

        if st.session_state.pet_slot_m2_1:
            pet = st.session_state.pet_slot_m2_1
            st.write("**Pet Equipado:**")
            try:
                st.image(pet["arquivo"], width=167)
            except Exception:
                st.warning(f"⚠️ Imagem ({pet['arquivo']}) não encontrada.")
            st.caption(f"{pet['nome']} | +{calcular_bonus_pet(pet):,} por clique")

    ch1_m2_o2, ch2_m2_o2, ch3_m2_o2 = calcular_chances_ovo(50, 35, 15)

    with col_m2_egg2:
        st.write("### Ovo Lendário:")
        st.write(f"{NOME_PET_M2_R1}: {ch1_m2_o2:.1f}% (+{BONUS_PET_M2_R1:,} Pts)")
        st.write(f"{NOME_PET_M2_R2}: {ch2_m2_o2:.1f}% (+{BONUS_PET_M2_R2:,} Pts)")
        st.write(f"{NOME_PET_M2_R3}: **{ch3_m2_o2:.1f}%** (+{BONUS_PET_M2_R3:,} Pts)")
        
        desativar_m2_ovo2 = st.session_state.pontos < CUSTO_OVO_MUNDO_2_CARO or loja_em_cooldown
        
        if st.button(f"Abrir Ovo = {CUSTO_OVO_MUNDO_2_CARO:,} Pontos", disabled=desativar_m2_ovo2, key="botao_m2_ovo2"):
            st.session_state.ultima_compra = time.time()
            if st.session_state.pontos >= CUSTO_OVO_MUNDO_2_CARO:
                st.session_state.pontos -= CUSTO_OVO_MUNDO_2_CARO
                sorteado = random.choices(
                   [{"nome": NOME_PET_M2_R1, "arquivo": "logo10.png", "bonus": BONUS_PET_M2_R1, "chance": "50%"}, 
                    {"nome": NOME_PET_M2_R2, "arquivo": "logo11.png", "bonus": BONUS_PET_M2_R2, "chance": "35%"},
                    {"nome": NOME_PET_M2_R3, "arquivo": "logo12.png", "bonus": BONUS_PET_M2_R3, "chance": "15%"}],
                   weights=[ch1_m2_o2, ch2_m2_o2, ch3_m2_o2], k=1
                )[0]
                st.session_state.pet_slot_m2_2 = sorteado
                atualizar_poder_clique()
                salvar_progresso_atual()
                time.sleep(0.5) 
                st.rerun()

        if st.session_state.pet_slot_m2_2:
            pet = st.session_state.pet_slot_m2_2
            st.write("**Pet Equipado:**")
            try:
                st.image(pet["arquivo"], width=120)
            except Exception:
                st.warning(f"⚠️ Imagem ({pet['arquivo']}) não encontrada.")
            st.caption(f"{pet['nome']} | +{calcular_bonus_pet(pet):,} por clique")

def get_leaderboard_data():
    return carregar_leaderboard()

# --- CONTEÚDO MUNDO 1 ---
if st.session_state.mundo_atual != 2:
    st.subheader("Primeiro Mundo")
    
    st.write("Trilha sonora: on/off")
    try:
        st.audio("musica67.mp3")
    except Exception:
        st.caption("🎵 Arquivo 'musica67.mp3' não encontrado.")

    renderizar_area_clique()

    st.markdown("---")
    st.subheader("Comprar Ovos:")
    col3, col4 = st.columns(2)

    ch1_m1_o1, ch2_m1_o1, ch3_m1_o1 = calcular_chances_ovo(50, 35, 15)

    with col3:
        st.write("### Ovo Comum:")
        st.write(f"Siruriru: {ch1_m1_o1:.1f}% (+1 Ponto)")
        st.write(f"Peppa Pig: {ch2_m1_o1:.1f}% (+5 Pontos)")
        st.write(f"Manoel G: **{ch3_m1_o1:.1f}%** (+10 Pontos)")
        
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
                   weights=[ch1_m1_o1, ch2_m1_o1, ch3_m1_o1], k=1
                )[0]
                st.session_state.pet_slot_1 = sorteado_ovo1
                atualizar_poder_clique()
                salvar_progresso_atual()
                time.sleep(0.5) 
                st.rerun()

        if st.session_state.pet_slot_1:
            pet = st.session_state.pet_slot_1
            st.write("**Pet Equipado:**")
            try:
                st.image(pet["arquivo"], width=188)
            except Exception:
                st.warning(f"⚠️ Imagem ({pet['arquivo']}) não encontrada.")
            st.caption(f"{pet['nome']} | +{calcular_bonus_pet(pet)} por clique")

    ch1_m1_o2, ch2_m1_o2, ch3_m1_o2 = calcular_chances_ovo(50, 35, 15)

    with col4:
        st.write("### Ovo Raro:")
        st.write(f"Dora A.: {ch1_m1_o2:.1f}% (+10 Pontos)")
        st.write(f"Sonic: {ch2_m1_o2:.1f}% (+50 Pontos)")
        st.write(f"Michael J.: **{ch3_m1_o2:.1f}%** (+100 Pontos)")
        
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
                   weights=[ch1_m1_o2, ch2_m1_o2, ch3_m1_o2], k=1
                )[0]
                st.session_state.pet_slot_2 = sorteado_ovo2
                atualizar_poder_clique()
                salvar_progresso_atual()
                time.sleep(0.5) 
                st.rerun()

        if st.session_state.pet_slot_2:
            pet = st.session_state.pet_slot_2
            st.write("**Pet Equipado:**")
            try:
                st.image(pet["arquivo"], width=100)
            except Exception:
                st.warning(f"⚠️ Imagem ({pet['arquivo']}) não encontrada.")
            st.caption(f"{pet['nome']} | +{calcular_bonus_pet(pet)} por clique")

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
                if st.session_state.pontos >= item['custo']:
                    st.session_state.ultima_compra = time.time()
                    st.session_state.pontos -= item['custo']
                    st.session_state.poder_base += item['qtd']
                    atualizar_poder_clique()  
                    st.session_state.pontos_leaderboard_cache = st.session_state.pontos
                    salvar_progresso_atual()
                    time.sleep(0.1)
                    st.rerun()

with col2:
    st.subheader("Auto Clickers")
    with st.container(height=350):
        for i, item in enumerate(melhorias_passivas):
            texto = f"+{item['qtd']:,}/s | {item['custo']:,} Pts"
            desativado = st.session_state.pontos < item['custo'] or loja_em_cooldown
            key_btn = f"p_{st.session_state.mundo_atual}_{i}"

            if st.button(texto, key=key_btn, disabled=desativado, use_container_width=True):
                if st.session_state.pontos >= item['custo']:
                    st.session_state.ultima_compra = time.time()
                    st.session_state.pontos -= item['custo']
                    st.session_state.pontos_por_segundo += item['qtd']
                    st.session_state.pontos_leaderboard_cache = st.session_state.pontos
                    salvar_progresso_atual()
                    time.sleep(0.1)
                    st.rerun()

atualizar_no_leaderboard(st.session_state.nome_usuario, st.session_state.pontos)

# --- LOG DE ATUALIZAÇÕES ---
st.markdown("---")
st.subheader("Atualizações:")
st.write("(1.0.0)(Beta) - Lançamento!!!")
st.write("(1.0.1) - Correção de bugs")
st.write("(1.1.2) - Adição dos Ovos, correção de bugs e preços balanceados")
st.write("(1.2.3) - Adição de novos pets e ovos e o log de updates")
st.write("(1.3.4) - Interface reformulada e correção de bugs")
st.write("(1.4.5) - Sistema de salvamento de jogo, adição de novos autoclickers, adição de um botão de reset e correção de bugs")
st.write("(1.5.6) - Adição do top global")
st.write("(1.6.7) - Adição do painel de adimin com senha e correção de bugs")
st.write("(1.7.8) - Adição do segundo mundo!!! novas melhorias, nova interface de melhorias, correção de bugs e muito mais!!!")
st.write("(1.8.9) - Adição de 2 novos ovos(segundo mundo), 6 novos pets e correção de bugs")
st.write("(2.0.0) - Adição de Sistema de login com senha e correção de bugs")
st.write("(2.1.1) - Sistema de salvamento de top global in tempo real, correção dos botões de ban, adicionar pontos e remover pontos(ADM) e correção de bugs")
st.write("(2.2.2) - Adição do Sistema de Mensagem Global (ADM)")
st.write("(2.3.3) - Adição de novas funções de multiplicação de sorte e dinheiro (ADM)")
st.write("(2.4.4) - Adição do Sistema de Inspeção de Jogadores (ADM)")
st.write("(2.5.5) - Remoção do login toda hora que você entrar")

# --- 🏆 TABELA DE CLASSIFICAÇÃO GLOBAL ---
st.markdown("---")
st.subheader("Top Global:")
dados_placar = get_leaderboard_data()

if dados_placar:
    st.table(dados_placar)
else:
    st.info("O placar está vazio.")

# --- SISTEMA DE RESET DE JOGO ---
st.markdown("---")
if not st.session_state.confirmando_reset:
    if st.button("Resetar Jogo", use_container_width=True):
        st.session_state.confirmando_reset = True
        st.rerun()
else:
    st.warning("⚠️ **Você tem certeza absoluta?** Isso apagará permanentemente todos os seus pontos, melhorias, mundos e pets salvos!")
    col_sim, col_nao = st.columns(2)
    
    with col_sim:
        if st.button("SIM, deletar tudo", type="primary", use_container_width=True):
            remover_jogador_leaderboard(st.session_state.nome_usuario)
            limpar_sessao_ativa()
            
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
            st.success("Jogo reiniciado com sucesso!")
            time.sleep(0.5)
            st.rerun()
            
    with col_nao:
        if st.button("NÃO, voltar ao jogo", use_container_width=True):
            st.session_state.confirmando_reset = False
            st.rerun()
