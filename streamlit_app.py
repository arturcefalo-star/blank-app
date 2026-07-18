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
SENHA_ADMIN2 = "19371937"
ACCOUNTS_FILE = "usuarios.json"
LEADERBOARD_FILE = "leaderboard.json"
AVISOS_FILE = "avisos.json"

# --- FUNÇÕES DE GERENCIAMENTO DE USUÁRIOS E SALVAMENTO ---

def carregar_todos_usuarios():
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                conteudo = json.load(f)
                return {k.lower(): v for k, v in conteudo.items()}
        except Exception:
            return {}
    return {}

def salvar_todos_usuarios(usuarios):
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        usuarios_normalizados = {k.lower(): v for k, v in usuarios.items()}
        json.dump(usuarios_normalizados, f, ensure_ascii=False, indent=4)

def salvar_progresso_atual(usando_admin=None, usando_apoiador=None):
    if st.session_state.logado and st.session_state.nome_usuario:
        usuarios = carregar_todos_usuarios()
        username_key = st.session_state.nome_usuario.lower()
        
        if username_key in usuarios:
            if usando_admin is not None:
                st.session_state.p_admin_ativo = usando_admin
            if usando_apoiador is not None:
                st.session_state.p_apoiador_ativo = usando_apoiador

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
                "mundo_atual": st.session_state.mundo_atual,
                "usando_admin": st.session_state.p_admin_ativo,
                "usando_apoiador": st.session_state.p_apoiador_ativo
            }
            salvar_todos_usuarios(usuarios)
            atualizar_no_leaderboard(usuarios[username_key]["nome_exibicao"], st.session_state.pontos)

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


# --- INICIALIZAÇÃO DE SESSÃO ---
if "logado" not in st.session_state:
    st.session_state.logado = False
if "nome_usuario" not in st.session_state:
    st.session_state.nome_usuario = ""

if not st.session_state.logado and "user_session" in st.query_params:
    usuario_salvo = st.query_params["user_session"].lower()
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
        st.session_state.p_admin_ativo = dados.get("usando_admin", False)
        st.session_state.p_apoiador_ativo = dados.get("usando_apoiador", False)
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
            
            if user_key in usuarios and str(usuarios[user_key]["senha"]).strip() == str(log_pass).strip():
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
                st.session_state.p_admin_ativo = dados.get("usando_admin", False)
                st.session_state.p_apoiador_ativo = dados.get("usando_apoiador", False)
                
                st.session_state.nome_usuario = usuarios[user_key]["nome_exibicao"]
                st.session_state.logado = True
                st.query_params["user_session"] = user_key
                
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
                    "senha": reg_pass.strip(),
                    "nome_exibicao": reg_user,
                    "dados": {
                        "pontos": 0, "poder_base": 1, "pontos_por_segundo": 0,
                        "pet_slot_1": None, "pet_slot_2": None,
                        "pet_slot_m2_1": None, "pet_slot_m2_2": None,
                        "ultimo_tick": time.time(), "mundo_2_desbloqueado": False, "mundo_atual": 1,
                        "usando_admin": False, "usando_apoiador": False
                    }
                }
                salvar_todos_usuarios(usuarios)
                atualizar_no_leaderboard(reg_user, 0)
                st.success("Conta criada com sucesso! Faça login na aba ao lado.")
                
    st.stop()

# =====================================================================
# 🎮 INTERFACE E LOGICA PRINCIPAL DO JOGO
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
if "p_admin_ativo" not in st.session_state:
    st.session_state.p_admin_ativo = False
if "p_apoiador_ativo" not in st.session_state:
    st.session_state.p_apoiador_ativo = False
if "jogador_sob_inspecao" not in st.session_state:
    st.session_state.jogador_sob_inspecao = ""

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

# Processamento passivo global de pontos
agora = time.time()
tempo_passado = agora - st.session_state.ultimo_tick
if tempo_passado >= 1.0:
    ciclos = int(tempo_passado)
    st.session_state.pontos += st.session_state.pontos_por_segundo * ciclos
    st.session_state.ultimo_tick = agora - (tempo_passado - ciclos)
    st.session_state.pontos_leaderboard_cache = st.session_state.pontos

atualizar_poder_clique()

# --- ÁREA DE CLIQUE FRAGMENTADA ---
@st.fragment
def renderizar_area_clique():
    st_autorefresh(interval=3000, key="game_click_loop")
    
    st.metric(label="Pontos Atuais", value=f"{st.session_state.pontos:,}")
    
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


# Sincronização em background do placar
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

# 🟢 FIX COOLDOWN: O Cooldown agora limpa dinamicamente ao invés de travar a thread
loja_em_cooldown = False
if (time.time() - st.session_state.ultima_compra) < 0.3:
    loja_em_cooldown = True

# --- BARRA LATERAL: LOGOUT, PAINEL ADMIN E TRAPAÇAS ---
with st.sidebar:
    st.write(f"Conectado como: **{st.session_state.nome_usuario}**")
    if st.button("Sair da Conta (Logout)", type="secondary"):
        salvar_progresso_atual(usando_admin=False, usando_apoiador=False)
        st.query_params.clear()
        st.session_state.logado = False
        st.session_state.nome_usuario = ""
        st.rerun()
        
    st.markdown("---")
    st.header("⚙️ Painel de Admin")
    
    modo_admin_chk = st.checkbox("Exibir Opções de Admin", value=st.session_state.p_admin_ativo)
    
    if not modo_admin_chk and st.session_state.p_admin_ativo:
        salvar_progresso_atual(usando_admin=False)
        st.rerun()
            
    if modo_admin_chk:
        senha_input = st.text_input("Digite a senha de Admin:", type="password", key="pwd_admin")
        
        if len(senha_input) > 0 and senha_input == SENHA_ADMIN:
            if not st.session_state.p_admin_ativo:
                salvar_progresso_atual(usando_admin=True)
                st.rerun()
                
            st.success("Acesso Autorizado!")
            
            # --- MONITOR DE UTILIZADORES ---
            st.markdown("---")
            st.subheader("👁️ Monitor de Painéis")
            db_usuarios = carregar_todos_usuarios()
            adms_ativos = [db_usuarios[k]["nome_exibicao"] for k in db_usuarios if db_usuarios[k].get("dados", {}).get("usando_admin", False)]
            apoiadores_ativos = [db_usuarios[k]["nome_exibicao"] for k in db_usuarios if db_usuarios[k].get("dados", {}).get("usando_apoiador", False)]
            
            st.write("**Utilizadores do painel de Admin:**")
            if adms_ativos:
                for adm in adms_ativos:
                    st.code(f"• {adm}", language="text")
            else:
                st.caption("Nenhum no momento.")
                
            st.write("**Utilizadores do painel de Apoiador:**")
            if apoiadores_ativos:
                for apo in apoiadores_ativos:
                    st.code(f"• {apo}", language="text")
            else:
                st.caption("Nenhum no momento.")
            st.markdown("---")
            
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

            # --- 🛠️ INSPEÇÃO DE JOGADORES - FIX DA SELEÇÃO ESTÁTICA ---
            st.markdown("---")
            st.subheader("Inspecionar Jogador")

            usuarios_db_inspect = carregar_todos_usuarios()
            lista_jogadores = sorted(list(set([usuarios_db_inspect[k]["nome_exibicao"] for k in usuarios_db_inspect if "nome_exibicao" in usuarios_db_inspect])))

            if lista_jogadores:
                # Mantém o jogador selecionado sem resetar o selectbox toda vez que a lista atualiza
                if st.session_state.jogador_sob_inspecao not in lista_jogadores:
                    st.session_state.jogador_sob_inspecao = lista_jogadores[0]
                
                idx_estatico = lista_jogadores.index(st.session_state.jogador_sob_inspecao)
                
                jogador_selecionado = st.selectbox(
                    "Selecione um jogador:", 
                    options=lista_jogadores, 
                    index=idx_estatico, 
                    key="live_inspect_static_v4"
                )
                st.session_state.jogador_sob_inspecao = jogador_selecionado

                if st.session_state.jogador_sob_inspecao:
                    alvo_atual = st.session_state.jogador_sob_inspecao
                    key_inspect = alvo_atual.lower()
                    
                    if key_inspect in usuarios_db_inspect:
                        dados_player = usuarios_db_inspect[key_inspect]["dados"]
                        
                        st.markdown(f"### Status de: **{alvo_atual}**")
                        
                        # Calculate total click power from targeted player for clarity
                        p_base_alvo = dados_player.get("poder_base", 1)
                        b1 = calcular_bonus_pet(dados_player.get("pet_slot_1"))
                        b2 = calcular_bonus_pet(dados_player.get("pet_slot_2"))
                        b3 = calcular_bonus_pet(dados_player.get("pet_slot_m2_1"))
                        b4 = calcular_bonus_pet(dados_player.get("pet_slot_m2_2"))
                        p_total_alvo = p_base_alvo + b1 + b2 + b3 + b4
                        
                        col_ins1, col_ins2, col_ins3 = st.columns(3)
                        col_ins1.metric("Pontos", f"{dados_player.get('pontos', 0):,}")
                        col_ins2.metric("Poder Base", f"{p_base_alvo:,}")
                        col_ins3.metric("Clique Total", f"{p_total_alvo:,}")
                        
                        st.metric("Pontos/Seg", f"{dados_player.get('pontos_por_segundo', 0):,}")
                        
                        mundo_txt = "Mundo 2" if dados_player.get("mundo_atual", 1) == 2 else "Mundo 1"
                        st.write(f" **Mundo:** {mundo_txt}")
                        
                        st.markdown(" **Pets Equipados:**")
                        p1 = dados_player.get("pet_slot_1")
                        p2 = dados_player.get("pet_slot_2")
                        pm1 = dados_player.get("pet_slot_m2_1")
                        pm2 = dados_player.get("pet_slot_m2_2")
                        st.text(f"• M1 S1: {p1['nome'] if p1 else 'Vazio'}")
                        st.text(f"• M1 S2: {p2['nome'] if p2 else 'Vazio'}")
                        st.text(f"• M2 S1: {pm1['nome'] if pm1 else 'Vazio'}")
                        st.text(f"• M2 S2: {pm2['nome'] if pm2 else 'Vazio'}")

                        st.markdown("---")
                        qtd_pontos = st.number_input("Quantidade de pontos (Add/Rem):", min_value=1, value=1000, step=100, key="qtd_pontos_adm")

                        col_adm1, col_adm2, col_adm3 = st.columns(3)
                        
                        if col_adm1.button("Ban", key=f"del_{key_inspect}", use_container_width=True):
                            usuarios_db_inspect[key_inspect]["dados"] = {
                                "pontos": 0, "poder_base": 1, "pontos_por_segundo": 0,
                                "pet_slot_1": None, "pet_slot_2": None,
                                "pet_slot_m2_1": None, "pet_slot_m2_2": None,
                                "ultimo_tick": time.time(), "mundo_2_desbloqueado": False, "mundo_atual": 1,
                                "usando_admin": False, "usando_apoiador": False
                            }
                            salvar_todos_usuarios(usuarios_db_inspect)
                            remover_jogador_leaderboard(alvo_atual)
                            st.rerun()
                        
                        if col_adm2.button("Add", key=f"add_{key_inspect}", use_container_width=True):
                            usuarios_db_inspect[key_inspect]["dados"]["pontos"] += qtd_pontos
                            salvar_todos_usuarios(usuarios_db_inspect)
                            if key_inspect == st.session_state.nome_usuario.lower():
                                st.session_state.pontos += qtd_pontos
                            atualizar_no_leaderboard(alvo_atual, usuarios_db_inspect[key_inspect]["dados"]["pontos"])
                            st.rerun()

                        if col_adm3.button("Rem", key=f"rem_{key_inspect}", use_container_width=True):
                            usuarios_db_inspect[key_inspect]["dados"]["pontos"] = max(0, usuarios_db_inspect[key_inspect]["dados"]["pontos"] - qtd_pontos)
                            salvar_todos_usuarios(usuarios_db_inspect)
                            if key_inspect == st.session_state.nome_usuario.lower():
                                st.session_state.pontos = max(0, st.session_state.pontos - qtd_pontos)
                            atualizar_no_leaderboard(alvo_atual, usuarios_db_inspect[key_inspect]["dados"]["pontos"])
                            st.rerun()
            else:
                st.info("Nenhum jogador cadastrado para inspecionar.")
                
            st.markdown("---")
            st.subheader("Eventos de admin")
            
            col_ev2x, col_ev3x = st.columns(2)
            if col_ev2x.button("Ativar 2X", key="btn_ev2"):
                config_globais["multiplicador_evento"] = 2
                salvar_configuracoes_globais(config_globais)
                st.rerun()
            if col_ev3x.button("Ativar 3X", key="btn_ev3"):
                config_globais["multiplicador_evento"] = 3
                salvar_configuracoes_globais(config_globais)
                st.rerun()
            
            if st.button("Desativar Eventos", type="secondary", use_container_width=True):
                config_globais["multiplicador_evento"] = 1
                config_globais["multiplicador_sorte"] = 1
                salvar_configuracoes_globais(config_globais)
                st.rerun()

        elif senha_input != "":
            st.error("Senha incorreta!")

    # --- MENU DE APOIADOR ---
    st.markdown("---")
    st.header("⚙️ Painel de Apoiador")
    modo_apoiador_chk = st.checkbox("Exibir Opções de Apoiador", value=st.session_state.p_apoiador_ativo)
    
    if modo_apoiador_chk:
        senha_cheat = st.text_input("Digite a senha de Apoiador:", type="password", key="pwd_cheat")
        if senha_cheat == SENHA_ADMIN2:
            st.success("Apoiador Verificado!")
            qtd_cheat = st.number_input("Adicionar Pontos:", min_value=1, value=5000, key="qtd_cheat_val")
            if st.button("Injetar Pontos", use_container_width=True):
                st.session_state.pontos += qtd_cheat
                salvar_progresso_atual()
                st.rerun()

# --- CONTROLE DE VIAGEM ENTRE MUNDOS ---
st.title("Clicker Game")

if aviso_sistema.strip() != "":
    st.info(f" **Mensagem do ADM:** {aviso_sistema}")

CUSTO_MUNDO_2 = 10000000

st.markdown("### Mundos:")
if not st.session_state.mundo_2_desbloqueado:
    if st.button(f"Comprar Mundo 2 (Custo: {CUSTO_MUNDO_2:,} Pts)", disabled=(st.session_state.pontos < CUSTO_MUNDO_2), use_container_width=True):
        st.session_state.pontos -= CUSTO_MUNDO_2
        st.session_state.mundo_2_desbloqueado = True
        st.session_state.mundo_atual = 2
        salvar_progresso_atual()
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
    st.subheader("Segundo mundo (2X Global)")
    renderizar_area_clique()

    st.markdown("---")
    st.subheader("Comprar ovos M2:")
    col_m2_egg1, col_m2_egg2 = st.columns(2)

    ch1_m2_o1, ch2_m2_o1, ch3_m2_o1 = calcular_chances_ovo(50, 35, 15)

    with col_m2_egg1:
        st.write(f"### Ovo Épico ({CUSTO_OVO_MUNDO_2_BARATO:,} pts):")
        if st.button("Abrir Ovo Épico", disabled=loja_em_cooldown, key="btn_m2_o1"):
            st.session_state.ultima_compra = time.time()
            if st.session_state.pontos >= CUSTO_OVO_MUNDO_2_BARATO:
                st.session_state.pontos -= CUSTO_OVO_MUNDO_2_BARATO
                st.session_state.pet_slot_m2_1 = random.choices(
                   [{"nome": NOME_PET_7, "arquivo": "logo7.png", "bonus": BONUS_PET_7}, 
                    {"nome": NOME_PET_8, "arquivo": "logo8.png", "bonus": BONUS_PET_8},
                    {"nome": NOME_PET_9, "arquivo": "logo9.png", "bonus": BONUS_PET_9}],
                   weights=[ch1_m2_o1, ch2_m2_o1, ch3_m2_o1], k=1
                )[0]
                atualizar_poder_clique()
                salvar_progresso_atual()
                st.rerun()

        if st.session_state.pet_slot_m2_1:
            st.caption(f"Equipado: {st.session_state.pet_slot_m2_1['nome']} (+{st.session_state.pet_slot_m2_1['bonus']:,})")

    with col_m2_egg2:
        st.write(f"### Ovo Lendário ({CUSTO_OVO_MUNDO_2_CARO:,} pts):")
        if st.button("Abrir Ovo Lendário", disabled=loja_em_cooldown, key="btn_m2_o2"):
            st.session_state.ultima_compra = time.time()
            if st.session_state.pontos >= CUSTO_OVO_MUNDO_2_CARO:
                st.session_state.pontos -= CUSTO_OVO_MUNDO_2_CARO
                st.session_state.pet_slot_m2_2 = random.choices(
                   [{"nome": NOME_PET_M2_R1, "arquivo": "logo10.png", "bonus": BONUS_PET_M2_R1}, 
                    {"nome": NOME_PET_M2_R2, "arquivo": "logo11.png", "bonus": BONUS_PET_M2_R2},
                    {"nome": NOME_PET_M2_R3, "arquivo": "logo12.png", "bonus": BONUS_PET_M2_R3}],
                   weights=[50, 35, 15], k=1
                )[0]
                atualizar_poder_clique()
                salvar_progresso_atual()
                st.rerun()

        if st.session_state.pet_slot_m2_2:
            st.caption(f"Equipado: {st.session_state.pet_slot_m2_2['nome']} (+{st.session_state.pet_slot_m2_2['bonus']:,})")

else:
    st.subheader("Primeiro Mundo")
    renderizar_area_clique()

    st.markdown("---")
    st.subheader("Comprar Ovos M1:")
    col3, col4 = st.columns(2)

    with col3:
        st.write("### Ovo Comum (100 pts):")
        if st.button("Abrir Ovo Comum", disabled=loja_em_cooldown, key="btn_m1_o1"):
            st.session_state.ultima_compra = time.time()
            if st.session_state.pontos >= 100:
                st.session_state.pontos -= 100
                st.session_state.pet_slot_1 = random.choices(
                   [{"nome": "Siruriru", "arquivo": "logo3.png", "bonus": 1}, 
                    {"nome": "Peppa Pig", "arquivo": "logo2.png", "bonus": 5},
                    {"nome": "Manoel G", "arquivo": "logo1.png", "bonus": 10}],
                   weights=[50, 35, 15], k=1
                )[0]
                atualizar_poder_clique()
                salvar_progresso_atual()
                st.rerun()
        if st.session_state.pet_slot_1:
            st.caption(f"Equipado: {st.session_state.pet_slot_1['nome']} (+{st.session_state.pet_slot_1['bonus']})")

    with col4:
        st.write("### Ovo Raro (1,000 pts):")
        if st.button("Abrir Ovo Raro", disabled=loja_em_cooldown, key="btn_m1_o2"):
            st.session_state.ultima_compra = time.time()
            if st.session_state.pontos >= 1000:
                st.session_state.pontos -= 1000
                st.session_state.pet_slot_2 = random.choices(
                   [{"nome": "Dora A.", "arquivo": "logo4.png", "bonus": 10}, 
                    {"nome": "Sonic", "arquivo": "logo5.png", "bonus": 50},
                    {"nome": "Michael J.", "arquivo": "logo6.png", "bonus": 100}],
                   weights=[50, 35, 15], k=1
                )[0]
                atualizar_poder_clique()
                salvar_progresso_atual()
                st.rerun()
        if st.session_state.pet_slot_2:
            st.caption(f"Equipado: {st.session_state.pet_slot_2['nome']} (+{st.session_state.pet_slot_2['bonus']})")

st.markdown("---")

# --- LOJA DE MELHORIAS ---
st.subheader("Loja de Melhorias")

if st.session_state.mundo_atual == 2:
    melhorias_clique = [{"qtd": 50000, "custo": 15000000}, {"qtd": 100000, "custo": 50000000}]
    melhorias_passivas = [{"qtd": 50000, "custo": 4000000}, {"qtd": 100000, "custo": 12000000}]
else:
    melhorias_clique = [{"qtd": 1, "custo": 100}, {"qtd": 5, "custo": 500}, {"qtd": 10, "custo": 1000}]
    melhorias_passivas = [{"qtd": 5, "custo": 200}, {"qtd": 10, "custo": 600}, {"qtd": 20, "custo": 1100}]

col1, col2 = st.columns(2)

with col1:
    st.subheader("Melhoria Clicker")
    for i, item in enumerate(melhorias_clique):
        if st.button(f"+{item['qtd']:,} clk | {item['custo']:,} Pts", key=f"clk_{i}", disabled=(st.session_state.pontos < item['custo'] or loja_em_cooldown)):
            st.session_state.ultima_compra = time.time()
            st.session_state.pontos -= item['custo']
            st.session_state.poder_base += item['qtd']
            atualizar_poder_clique()
            salvar_progresso_atual()
            st.rerun()

with col2:
    st.subheader("Auto Clickers")
    for i, item in enumerate(melhorias_passivas):
        if st.button(f"+{item['qtd']:,}/s | {item['custo']:,} Pts", key=f"pas_{i}", disabled=(st.session_state.pontos < item['custo'] or loja_em_cooldown)):
            st.session_state.ultima_compra = time.time()
            st.session_state.pontos -= item['custo']
            st.session_state.pontos_por_segundo += item['qtd']
            salvar_progresso_atual()
            st.rerun()

# Placar e Logs finais
if st.session_state.nome_usuario:
    atualizar_no_leaderboard(st.session_state.nome_usuario, st.session_state.pontos)

st.markdown("---")
st.subheader("Top Global:")
dados_placar = carregar_leaderboard()
if dados_placar:
    st.table(dados_placar)
