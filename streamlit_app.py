import streamlit as st
import time
import random
import json
import os
import uuid
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# Configuração da página precisa ser a primeira linha Streamlit
st.set_page_config(page_title="Clicker Game", layout="centered")

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

SENHA_DEV = "--$3CR3T--"  
SENHA_ADMIN = "XXxx67xxXX"
SENHA_APOIADOR = "67AP0IO67"  
ACCOUNTS_FILE = "usuarios.json"
LEADERBOARD_FILE = "leaderboard.json"
AVISOS_FILE = "avisos.json"

# --- CONFIGURAÇÃO DO POOL DE TOTENS ---
TOTENS_DISPONIVEIS = [
    {"nome": "Totem de Madeira", "raridade": "Comum", "multiplicador": 1.2, "custo": 500, "chance": 40},
    {"nome": "Totem de Pedra", "raridade": "Comum", "multiplicador": 1.5, "custo": 2500, "chance": 25},
    {"nome": "Totem de Ferro", "raridade": "Raro", "multiplicador": 2.0, "custo": 15000, "chance": 15},
    {"nome": "Totem de Ouro", "raridade": "Raro", "multiplicador": 77000, "custo": 75000, "chance": 10},
    {"nome": "Totem de Diamante", "raridade": "Épico", "multiplicador": 5.0, "custo": 500000, "chance": 6},
    {"nome": "Totem de Obsidiana", "raridade": "Lendário", "multiplicador": 7.5, "custo": 5000000, "chance": 3},
    {"nome": "Totem Mítico do Olimpo", "raridade": "Mítico", "multiplicador": 10.0, "custo": 50000000, "chance": 1}
]

# --- FUNÇÕES DE GERENCIAMENTO DE USUÁRIOS NO SERVIDOR ---

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

def tem_titulo(titulo_necessario):
    if not st.session_state.get("logado") or not st.session_state.get("nome_usuario"):
        return False
    usuarios = carregar_todos_usuarios()
    user_key = st.session_state.nome_usuario.lower()
    if user_key in usuarios:
        return usuarios[user_key]["dados"].get("titulo") == titulo_necessario
    return False

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
                "totem_equipado": st.session_state.totem_equipado,
                "ultimo_tick": st.session_state.ultimo_tick,
                "mundo_2_desbloqueado": st.session_state.mundo_2_desbloqueado,
                "mundo_atual": st.session_state.mundo_atual,
                "titulo": usuarios[username_key]["dados"].get("titulo", "")
            }
            usuarios[username_key]["ultimo_login"] = time.strftime("%Y-%m-%d %H:%M:%S")
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

def resetar_estados_jogador_local():
    st.session_state.logado = False
    st.session_state.nome_usuario = ""
    st.session_state.pontos = 0
    st.session_state.poder_base = 1
    st.session_state.pontos_por_segundo = 0
    st.session_state.pet_slot_1 = None
    st.session_state.pet_slot_2 = None
    st.session_state.pet_slot_m2_1 = None
    st.session_state.pet_slot_m2_2 = None
    st.session_state.totem_equipado = None
    st.session_state.mundo_2_desbloqueado = False
    st.session_state.mundo_atual = 1
    st.session_state.titulo = ""
    st.session_state.pontos_leaderboard_cache = 0
    atualizar_poder_clique()

# --- COMPONENTE JAVASCRIPT CORRIGIDO ---
def injetar_js_localstorage():
    js_code = """
    <script>
    const parentDoc = window.parent.document;
    
    function sincronizar() {
        let contas = localStorage.getItem("clicker_saved_accounts") || "{}";
        const streamlitInput = parentDoc.querySelector('input[aria-label="bridge_storage_input"]');
        if (streamlitInput && streamlitInput.value !== contas) {
            if (contas !== "{}") {
                streamlitInput.value = contas;
                streamlitInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
    }

    window.addEventListener("message", function(event) {
        if (event.data.type === "SAVE_ACCOUNT") {
            let contas = JSON.parse(localStorage.getItem("clicker_saved_accounts") || "{}");
            contas[event.data.user.toLowerCase()] = {
                usuario: event.data.user, 
                senha: event.data.password,
                dados_completos: event.data.dados_completos
            };
            localStorage.setItem("clicker_saved_accounts", JSON.stringify(contas));
            sincronizar();
        }
        if (event.data.type === "REMOVE_ACCOUNT") {
            let contas = JSON.parse(localStorage.getItem("clicker_saved_accounts") || "{}");
            delete contas[event.data.user.toLowerCase()];
            localStorage.setItem("clicker_saved_accounts", JSON.stringify(contas));
            sincronizar();
        }
    });

    setTimeout(sincronizar, 100);
    setInterval(sincronizar, 1000);
    </script>
    """
    components.html(js_code, height=0, width=0)

# --- INICIALIZAÇÃO DE SESSÃO ---

if "logado" not in st.session_state:
    st.session_state.logado = False
if "nome_usuario" not in st.session_state:
    st.session_state.nome_usuario = ""

bridge_data = st.text_input("bridge_storage_input", key="bridge_storage_input", label_visibility="collapsed")
injetar_js_localstorage()

try:
    contas_locais = json.loads(bridge_data) if bridge_data else {}
    if contas_locais:
        usuarios_server = carregar_todos_usuarios()
        alterou = False
        for k, v in contas_locais.items():
            if k not in usuarios_server:
                usuarios_server[k] = v["dados_completos"]
                alterou = True
        if alterou:
            salvar_todos_usuarios(usuarios_server)
except Exception:
    contas_locais = {}

todos_usuarios_server = carregar_todos_usuarios()
for k, v in contas_locais.items():
    if k not in todos_usuarios_server:
        todos_usuarios_server[k] = v["dados_completos"]
salvar_todos_usuarios(todos_usuarios_server)


# =====================================================================
# 🔐 TELA DE LOGIN / REGISTRO
# =====================================================================
if not st.session_state.logado:
    st.title("Clicker Game - Login")
    
    aba_login, aba_salvas, aba_registro = st.tabs(["Entrar na Conta", "Contas Já Criadas 💾", "Criar Nova Conta"])
    
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
                st.session_state.totem_equipado = dados.get("totem_equipado", None)
                st.session_state.ultimo_tick = dados.get("ultimo_tick", time.time())
                st.session_state.mundo_2_desbloqueado = dados.get("mundo_2_desbloqueado", False)
                st.session_state.mundo_atual = dados.get("mundo_atual", 1)
                st.session_state.titulo = dados.get("titulo", "")
                st.session_state.pontos_leaderboard_cache = dados.get("pontos", 0)
                
                st.session_state.nome_usuario = usuarios[user_key]["nome_exibicao"]
                st.session_state.logado = True
                
                st.session_state["tmp_logged_password"] = log_pass
                
                st.components.v1.html(f"""
                <script>
                window.parent.postMessage({{
                    type: "SAVE_ACCOUNT", 
                    user: "{usuarios[user_key]['nome_exibicao']}", 
                    password: "{log_pass}",
                    dados_completos: {json.dumps(usuarios[user_key])}
                }}, "*");
                </script>
                """, height=0, width=0)
                
                st.success(f"Bem-vindo de volta, {st.session_state.nome_usuario}!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

    with aba_salvas:
        st.subheader("Entrar com Conta já Criada no Servidor")
        
        todos_usuarios_server = carregar_todos_usuarios()
        
        if todos_usuarios_server:
            opcoes_contas = [dados["nome_exibicao"] for dados in todos_usuarios_server.values()]
            conta_selecionada = st.selectbox("Escolha uma das contas registradas:", opcoes_contas)
            key_selecionada = conta_selecionada.lower()
            
            st.markdown(f"Para acessar **{conta_selecionada}**, confirme a senha de acesso:")
            senha_confirmacao = st.text_input("Senha da Conta:", type="password", key="confirm_local_pass")
            
            col_entrar, col_remover = st.columns([2, 1])
            
            if col_entrar.button("Confirmar e Entrar", type="primary", use_container_width=True):
                senha_salva = todos_usuarios_server[key_selecionada]["senha"]
                
                if senha_confirmacao == senha_salva:
                    dados = todos_usuarios_server[key_selecionada]["dados"]
                    st.session_state.pontos = dados.get("pontos", 0)
                    st.session_state.poder_base = dados.get("poder_base", 1)
                    st.session_state.pontos_por_segundo = dados.get("pontos_por_segundo", 0)
                    st.session_state.pet_slot_1 = dados.get("pet_slot_1", None)
                    st.session_state.pet_slot_2 = dados.get("pet_slot_2", None)
                    st.session_state.pet_slot_m2_1 = dados.get("pet_slot_m2_1", None)
                    st.session_state.pet_slot_m2_2 = dados.get("pet_slot_m2_2", None)
                    st.session_state.totem_equipado = dados.get("totem_equipado", None)
                    st.session_state.ultimo_tick = dados.get("ultimo_tick", time.time())
                    st.session_state.mundo_2_desbloqueado = dados.get("mundo_2_desbloqueado", False)
                    st.session_state.mundo_atual = dados.get("mundo_atual", 1)
                    st.session_state.titulo = dados.get("titulo", "")
                    st.session_state.pontos_leaderboard_cache = dados.get("pontos", 0)
                    
                    st.session_state.nome_usuario = todos_usuarios_server[key_selecionada]["nome_exibicao"]
                    st.session_state.logado = True
                    st.session_state["tmp_logged_password"] = senha_salva
                    
                    todos_usuarios_server[key_selecionada]["ultimo_login"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    salvar_todos_usuarios(todos_usuarios_server)
                    
                    st.success(f"Olá, {st.session_state.nome_usuario}!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Senha incorreta para a conta selecionada!")
                    
            if col_remover.button("Remover da Lista ❌", use_container_width=True):
                del todos_usuarios_server[key_selecionada]
                salvar_todos_usuarios(todos_usuarios_server)
                remover_jogador_leaderboard(key_selecionada)
                st.components.v1.html(f"""<script>window.parent.postMessage({{type: "REMOVE_ACCOUNT", user: "{key_selecionada}"}}, "*");</script>""", height=0, width=0)
                st.toast("Conta deletada do servidor!")
                time.sleep(0.5)
                st.rerun()
        else:
            st.info("Nenhuma conta cadastrada no servidor ainda. Crie uma nova conta na aba ao lado.")
                
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
                nova_conta = {
                    "senha": reg_pass,
                    "nome_exibicao": reg_user,
                    "ultimo_login": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "dados": {
                        "pontos": 0, "poder_base": 1, "pontos_por_segundo": 0,
                        "pet_slot_1": None, "pet_slot_2": None,
                        "pet_slot_m2_1": None, "pet_slot_m2_2": None, "totem_equipado": None,
                        "ultimo_tick": time.time(), "mundo_2_desbloqueado": False, "mundo_atual": 1,
                        "titulo": ""
                    }
                }
                usuarios[user_key] = nova_conta
                salvar_todos_usuarios(usuarios)
                
                st.components.v1.html(f"""
                <script>
                window.parent.postMessage({{
                    type: "SAVE_ACCOUNT", 
                    user: "{reg_user}", 
                    password: "{reg_pass}",
                    dados_completos: {json.dumps(nova_conta)}
                }}, "*");
                </script>
                """, height=0, width=0)
                
                st.success("Conta criada com sucesso!")
                time.sleep(0.5)
                st.rerun()
                
    st.stop()

# =====================================================================
# 🎮 INTERFACE E LÓGICA PRINCIPAL DO JOGO
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
if "totem_equipado" not in st.session_state:
    st.session_state.totem_equipado = None

usuarios_temp = carregar_todos_usuarios()
user_key_temp = st.session_state.nome_usuario.lower()
if user_key_temp in usuarios_temp:
    st.session_state.titulo = usuarios_temp[user_key_temp]["dados"].get("titulo", "")
    st.session_state.totem_equipado = usuarios_temp[user_key_temp]["dados"].get("totem_equipado", None)
else:
    st.session_state.titulo = ""
    st.session_state.totem_equipado = None

config_globais = carregar_configuracoes_globais()
aviso_sistema = config_globais.get("mensagem", "")
mult_evento = config_globais.get("multiplicador_evento", 1) 
mult_sorte = config_globais.get("multiplicador_sorte", 1)

def obter_totens_da_rodada():
    minuto_atual = int(time.time() / 300) 
    random.seed(minuto_atual)
    
    totens_escolhidos = []
    pool_copia = list(TOTENS_DISPONIVEIS)
    
    for _ in range(3):
        if not pool_copia:
            break
        pesos = [t["chance"] for t in pool_copia]
        sorteado = random.choices(pool_copia, weights=pesos, k=1)[0]
        totens_escolhidos.append(sorteado)
        pool_copia.remove(sorteado)
        
    random.seed() 
    return totens_escolhidos

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
    
    if st.session_state.totem_equipado:
        poder_calculado = int(poder_calculado * st.session_state.totem_equipado["multiplicador"])
        
    st.session_state.poder_clique = poder_calculado * mult_evento

def calcular_chances_ovo(c1, c2, c3_base):
    c3_atual = min(c3_base * mult_sorte, 90)
    restante = 100 - c3_atual
    soma_base_comuns = c1 + c2
    
    c1_atual = (c1 / soma_base_comuns) * restante
    c2_atual = (c2 / soma_base_comuns) * restante
    return c1_atual, c2_atual, c3_atual

atualizar_poder_clique()

# --- SISTEMA DE CLIQUE E AUTO-CLICKER (REESTRUTURADO) ---
@st.fragment
def renderizar_area_clique():
    # Atualizador automático de 1 segundo (Soma o Auto-click em tempo real)
    st_autorefresh(interval=1000, key="auto_click_timer")
    
    agora = time.time()
    tempo_passado = agora - st.session_state.ultimo_tick
    if tempo_passado >= 1.0:
        ciclos = int(tempo_passado)
        st.session_state.pontos += st.session_state.pontos_por_segundo * ciclos
        st.session_state.ultimo_tick = agora - (tempo_passado - ciclos)
        st.session_state.pontos_leaderboard_cache = st.session_state.pontos
        salvar_progresso_atual()

    st.metric(label="Pontos Atuais", value=f"{st.session_state.pontos:,}")
    
    if st.session_state.totem_equipado:
        st.write(f"🌟 **Totem Ativo:** {st.session_state.totem_equipado['nome']} ({st.session_state.totem_equipado['multiplicador']}x Crítico)")
    
    if st.session_state.mundo_atual == 2:
        if st.button("            Click Here          ", key="click_m2_btn", use_container_width=True):
            st.session_state.pontos += (st.session_state.poder_clique * 2)
            st.session_state.pontos_leaderboard_cache = st.session_state.pontos
            salvar_progresso_atual()
        st.write(f"**Poder de clique:** {(st.session_state.poder_clique * 2):,} (2X do Mundo)")
    else:
        if st.button("            Click Here          ", key="click_m1_btn", use_container_width=True):
            st.session_state.pontos += st.session_state.poder_clique
            st.session_state.pontos_leaderboard_cache = st.session_state.pontos
            salvar_progresso_atual()
        st.write(f"**Poder de clique:** {st.session_state.poder_clique:,}")
        
    st.write(f"**Pontos por segundo:** {st.session_state.pontos_por_segundo:,}")

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

# --- BARRA LATERAL ---
with st.sidebar:
    prefixo_exibicao = f"[{st.session_state.titulo}] " if st.session_state.titulo else ""
    st.write(f"Conectado como: **{prefixo_exibicao}{st.session_state.nome_usuario}**")
    
    st.caption("✓ Conta sincronizada no navegador.")
    if st.button("🔄 Forçar Redundância Manual", use_container_width=True):
        usuarios = carregar_todos_usuarios()
        key_user = st.session_state.nome_usuario.lower()
        if key_user in usuarios:
            st.components.v1.html(f"""
            <script>
            window.parent.postMessage({{
                type: "SAVE_ACCOUNT", 
                user: "{st.session_state.nome_usuario}", 
                password: "{st.session_state.get('tmp_logged_password','')}",
                dados_completos: {json.dumps(usuarios[key_user])}
            }}, "*");
            </script>
            """, height=0, width=0)
            st.toast("Backup local updated!")

    if st.button("Sair da Conta (Logout)", type="secondary", use_container_width=True):
        salvar_progresso_atual()
        resetar_estados_jogador_local()
        st.rerun()
        
    st.markdown("---")

    # 💻 PAINEL DE DEV
    st.header("⚙️ Painel de Desenvolvedor")
    exibir_painel_dev = False
    
    if st.checkbox("Ativar Modo Desenvolver"):
        senha_dev_input = st.text_input("Digite a senha de Desenvolvedor:", type="password", key="senha_dev_input")
        if len(senha_dev_input) > 0:
            if senha_dev_input == SENHA_DEV:
                st.success("Success!")
                exibir_painel_dev = True
            else:
                st.error("Senha de Desenvolvedor incorreta!")

    if exibir_painel_dev:
        st.subheader("Modificador de status")
        qtd_alteracao = st.number_input("Valor da Alteração:", min_value=1, value=10000, step=1000, key="dev_val_attr")
        
        st.subheader("Gerenciamento Geral (Banco de Dados)")
        placar_completo_dev = []
        if os.path.exists(LEADERBOARD_FILE):
            try:
                with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                    placar_completo_dev = json.load(f)
            except Exception:
                pass

        if placar_completo_dev:
            usuarios_db_dev = carregar_todos_usuarios()
            for i, jogador in enumerate(placar_completo_dev):
                name_jogador = jogador["Jogador"]
                key_jogador = name_jogador.lower()
                
                titulo_atual = ""
                if key_jogador in usuarios_db_dev:
                    titulo_atual = usuarios_db_dev[key_jogador]["dados"].get("titulo", "")
                
                prefixo_lista = f"[{titulo_atual}] " if titulo_atual else ""
                st.write(f"**{prefixo_lista}{name_jogador}**")
                
                col_dev_pts, col_dev_clk, col_dev_pps, col_dev_t, col_dev_ban = st.columns([1, 1, 1, 1.2, 0.8])
                
                if col_dev_pts.button("Pontos", key=f"dev_pts_{key_jogador}_{i}"):
                    if key_jogador in usuarios_db_dev:
                        usuarios_db_dev[key_jogador]["dados"]["pontos"] = max(0, usuarios_db_dev[key_jogador]["dados"].get("pontos", 0) + qtd_alteracao)
                        salvar_todos_usuarios(usuarios_db_dev)
                    if key_jogador == st.session_state.nome_usuario.lower():
                        st.session_state.pontos += qtd_alteracao
                        st.session_state.pontos_leaderboard_cache = st.session_state.pontos
                    for j in placar_completo_dev:
                        if j["Jogador"].lower() == key_jogador:
                            j["Pontos"] = max(0, j.get("Pontos", 0) + qtd_alteracao)
                            break
                    salvar_leaderboard_completo(placar_completo_dev)
                    st.rerun()
                    
                if col_dev_clk.button("Poder/C", key=f"dev_clk_{key_jogador}_{i}"):
                    if key_jogador in usuarios_db_dev:
                        usuarios_db_dev[key_jogador]["dados"]["poder_base"] = max(1, usuarios_db_dev[key_jogador]["dados"].get("poder_base", 1) + qtd_alteracao)
                        salvar_todos_usuarios(usuarios_db_dev)
                    if key_jogador == st.session_state.nome_usuario.lower():
                        st.session_state.poder_base += qtd_alteracao
                        atualizar_poder_clique()
                    st.success("Poder de clique updated!")
                    st.rerun()

                if col_dev_pps.button("Pontos/s", key=f"dev_pps_{key_jogador}_{i}"):
                    if key_jogador in usuarios_db_dev:
                        usuarios_db_dev[key_jogador]["dados"]["pontos_por_segundo"] = max(0, usuarios_db_dev[key_jogador]["dados"].get("pontos_por_segundo", 0) + qtd_alteracao)
                        salvar_todos_usuarios(usuarios_db_dev)
                    if key_jogador == st.session_state.nome_usuario.lower():
                        st.session_state.pontos_por_segundo += qtd_alteracao
                    st.success("Pontos/Seg updated!")
                    st.rerun()

                with col_dev_t.popover("Title", use_container_width=True):
                    opcoes_titulos_dev = ["Nenhum", "DEV", "ADM", "APD"]
                    try:
                        idx_atual = opcoes_titulos_dev.index(titulo_atual) if titulo_atual in opcoes_titulos_dev else 0
                    except ValueError:
                        idx_atual = 0
                    opcao_titulo = st.selectbox("Escolha:", opcoes_titulos_dev, key=f"sel_dev_t_{key_jogador}_{i}", index=idx_atual)
                    if st.button("Aplicar", key=f"btn_dev_t_{key_jogador}_{i}", use_container_width=True):
                        if key_jogador in usuarios_db_dev:
                            novo_t = "" if opcao_titulo == "Nenhum" else opcao_titulo
                            usuarios_db_dev[key_jogador]["dados"]["titulo"] = novo_t
                            salvar_todos_usuarios(usuarios_db_dev)
                            if key_jogador == st.session_state.nome_usuario.lower():
                                st.session_state.titulo = novo_t
                            st.success("Título Salvo!")
                            time.sleep(0.3)
                            st.rerun()

                if col_dev_ban.button("Ban", key=f"dev_ban_{key_jogador}_{i}"):
                    if key_jogador in usuarios_db_dev:
                        del usuarios_db_dev[key_jogador]
                        salvar_todos_usuarios(usuarios_db_dev)
                    placar_completo_dev = [j for j in placar_completo_dev if j["Jogador"].lower() != key_jogador]
                    salvar_leaderboard_completo(placar_completo_dev)
                    if key_jogador == st.session_state.nome_usuario.lower():
                        resetar_estados_jogador_local()
                    st.rerun()
                st.markdown("---")

        st.subheader("Inspecionar Jogador")
        usuarios_db_inspect = carregar_todos_usuarios()
        mapeamento_jogadores = {usuarios_db_inspect[k]["nome_exibicao"]: k for k in usuarios_db_inspect if "nome_exibicao" in usuarios_db_inspect[k]}
        lista_jogadores = list(mapeamento_jogadores.keys())

        if lista_jogadores:
            jogador_selecionado = st.selectbox("Selecione um jogador do banco de dados:", lista_jogadores, key="inspect_select")
            if st.button("Inspecionar Dados", use_container_width=True, key="btn_inspect_action"):
                key_inspect = mapeamento_jogadores[jogador_selecionado]
                dados_player = usuarios_db_inspect[key_inspect]["dados"]
                visto_ultimo = usuarios_db_inspect[key_inspect].get("ultimo_login", "Não registrado")
                
                st.markdown(f"### Status de: **{jogador_selecionado}**")
                st.write(f" **Último Login Realizado:** {visto_ultimo}")
                
                col_ins1, col_ins2, col_ins3 = st.columns(3)
                col_ins1.metric("Pontos", f"{dados_player.get('pontos', 0):,}")
                col_ins2.metric("Poder Base", f"{dados_player.get('poder_base', 1):,}")
                col_ins3.metric("Pontos/Seg", f"{dados_player.get('pontos_por_segundo', 0):,}")
                
                mundo_txt = "Mundo 2" if dados_player.get("mundo_atual", 1) == 2 else "Mundo 1"
                m2_liberado = "Sim" if dados_player.get("mundo_2_desbloqueado", False) else "Não"
                st.write(f" **Mundo Atual:** {mundo_txt} |  **Mundo 2 Desbloqueado?** {m2_liberado}")
                
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
                    st.write(f"Slot 1: {pm1['nome']} (+{pm1['bonus']:,})" if pm1 else "Slot 1: Vazio")
                    st.write(f"Slot 2: {pm2['nome']} (+{pm2['bonus']:,})" if pm2 else "Slot 2: Vazio")
                
                st.markdown(" **Totem Equipado:**")
                tot_player = dados_player.get("totem_equipado")
                st.write(f"{tot_player['nome']} ({tot_player['multiplicador']}x)" if tot_player else "Nenhum Totem Equipado")
        
    st.markdown("---")
    
    # ⚙️ PAINEL DE ADMIN
    st.header("⚙️ Painel de Admin")
    acesso_admin = tem_titulo("ADM") or tem_titulo("DEV")
    exibir_painel_admin = False
    
    if acesso_admin:
        st.success(f"Acesso automático concedido via título [{st.session_state.titulo}]!")
        exibir_painel_admin = True
    else:
        if st.checkbox("Ativar Modo Administrador"):
            senha_input = st.text_input("Digite a senha de Admin:", type="password", key="senha_admin_input")
            if len(senha_input) > 0:
                if senha_input == SENHA_ADMIN:
                    st.success("Success!")
                    exibir_painel_admin = True
                else:
                    st.error("Senha incorreta!")
                    
    if exibir_painel_admin:
        st.subheader("Modificador de Pontos")
        qtd_pontos = st.number_input("Quantidade de pontos para Add/Rem:", min_value=1, value=1000, step=100, key="admin_pt_val")
        
        st.subheader("Gerenciar Placar Global")
        placar_completo = []
        if os.path.exists(LEADERBOARD_FILE):
            try:
                with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                    placar_completo = json.load(f)
            except Exception:
                pass

        if placar_completo:
            usuarios_db = carregar_todos_usuarios()
            for i, player in enumerate(placar_completo):
                name_jogador = player["Jogador"]
                key_jogador = name_jogador.lower()
                
                titulo_atual = ""
                if key_jogador in usuarios_db:
                    titulo_atual = usuarios_db[key_jogador]["dados"].get("titulo", "")
                
                prefixo_lista = f"[{titulo_atual}] " if titulo_atual else ""
                
                col_adm1, col_adm3, col_adm4 = st.columns([2, 1, 1])
                col_adm1.write(f"**{prefixo_lista}{name_jogador}**: {player['Pontos']:,} pts")
                
                if col_adm3.button("Add", key=f"add_{key_jogador}_{i}"):
                    if key_jogador in usuarios_db:
                        usuarios_db[key_jogador]["dados"]["pontos"] = max(0, usuarios_db[key_jogador]["dados"].get("pontos", 0) + qtd_pontos)
                        salvar_todos_usuarios(usuarios_db)
                    if key_jogador == st.session_state.nome_usuario.lower():
                        st.session_state.pontos += qtd_pontos
                        st.session_state.pontos_leaderboard_cache = st.session_state.pontos
                    for j in placar_completo:
                        if j["Jogador"].lower() == key_jogador:
                            j["Pontos"] = max(0, j.get("Pontos", 0) + qtd_pontos)
                            break
                    salvar_leaderboard_completo(placar_completo)
                    st.rerun()

                if col_adm4.button("Rem", key=f"rem_{key_jogador}_{i}"):
                    if key_jogador in usuarios_db:
                        usuarios_db[key_jogador]["dados"]["pontos"] = max(0, usuarios_db[key_jogador]["dados"].get("pontos", 0) - qtd_pontos)
                        salvar_todos_usuarios(usuarios_db)
                    if key_jogador == st.session_state.nome_usuario.lower():
                        st.session_state.pontos = max(0, st.session_state.pontos - qtd_pontos)
                        st.session_state.pontos_leaderboard_cache = st.session_state.pontos
                    for j in placar_completo:
                        if j["Jogador"].lower() == key_jogador:
                            j["Pontos"] = max(0, j.get("Pontos", 0) - qtd_pontos)
                            break
                    salvar_leaderboard_completo(placar_completo)
                    st.rerun()

        st.markdown("---")
        st.subheader("Mensagem Global")
        nova_msg = st.text_input("Texto Global:", value=aviso_sistema, placeholder="Digite o aviso geral aqui...", key="admin_msg_field")
        
        col_msg1, col_msg2 = st.columns(2)
        if col_msg1.button("Enviar Mensagem", use_container_width=True, key="admin_send_msg"):
            config_globais["mensagem"] = nova_msg
            salvar_configuracoes_globais(config_globais)
            st.success("Mensagem enviada!")
            time.sleep(0.3)
            st.rerun()
            
        if col_msg2.button("Apagar", type="secondary", use_container_width=True, key="admin_clear_msg"):
            config_globais["mensagem"] = ""
            salvar_configuracoes_globais(config_globais)
            st.rerun()

        st.markdown("---")
        st.subheader("Eventos de Admin")
        
        status_evento = f"ATIVADO ({mult_evento}X)" if mult_evento > 1 else "DESATIVADO"
        st.write(f"Multiplicador de Dinheiro: **{status_evento}**")
        
        col_ev2x, col_ev3x, col_ev4x, col_ev5x = st.columns(4)
        if col_ev2x.button("Ativar 2X", key="btn_ev2", use_container_width=True, disabled=(mult_evento == 2)):
            config_globais["multiplicador_evento"] = 2
            salvar_configuracoes_globais(config_globais)
            st.rerun()
        if col_ev3x.button("Ativar 3X", key="btn_ev3", use_container_width=True, disabled=(mult_evento == 3)):
            config_globais["multiplicador_evento"] = 3
            salvar_configuracoes_globais(config_globais)
            st.rerun()
        if col_ev4x.button("Ativar 4X", key="btn_ev4", use_container_width=True, disabled=(mult_evento == 4)):
            config_globais["multiplicador_evento"] = 4
            salvar_configuracoes_globais(config_globais)
            st.rerun()
        if col_ev5x.button("Ativar 5X", key="btn_ev5", use_container_width=True, disabled=(mult_evento == 5)):
            config_globais["multiplicador_evento"] = 5
            salvar_configuracoes_globais(config_globais)
            st.rerun()
        
        if st.button("Desativar", type="secondary", use_container_width=True, disabled=(mult_evento == 1), key="btn_desativar_evento"):
            config_globais["multiplicador_evento"] = 1
            salvar_configuracoes_globais(config_globais)
            st.rerun()

    st.markdown("---")

    # --- PAINEL DE APOIADOR ---
    st.header("⚙️ Painel de Apoiador")
    acesso_apoiador = tem_titulo("APD") or tem_titulo("ADM") or tem_titulo("DEV")
    exibir_painel_apoiador = False
    
    if acesso_apoiador:
        st.success(f"Acesso automático concedido via título [{st.session_state.titulo}]!")
        exibir_painel_apoiador = True
    else:
        if st.checkbox("Ativar Modo Apoiador"):
            senha_apoio_input = st.text_input("Digite a senha de Apoiador:", type="password", key="senha_apoio_input")
            if len(senha_apoio_input) > 0:
                if senha_apoio_input == SENHA_APOIADOR:
                    st.success("Success!")
                    exibir_painel_apoiador = True
                else:
                    st.error("Senha de apoiador incorreta!")
                    
    if exibir_painel_apoiador:
        st.subheader("Add/Rem seus pontos")
        qtd_pontos_apoio = st.number_input("Quantidade de pontos para Add/Rem:", min_value=1, value=50000, step=1000, key="qtd_pontos_apoio")
        
        col_apoio1, col_apoio2, col_apoio3 = st.columns([2, 1, 1])
        col_apoio1.write(f"**Você {st.session_state.nome_usuario}**: {st.session_state.pontos:,} pts")
        
        if col_apoio2.button("Add", key="add_pontos_apoio", use_container_width=True):
            usuarios_db = carregar_todos_usuarios()
            key_jogador = st.session_state.nome_usuario.lower()
            if key_jogador in usuarios_db:
                usuarios_db[key_jogador]["dados"]["pontos"] = max(0, usuarios_db[key_jogador]["dados"].get("pontos", 0) + qtd_pontos_apoio)
                salvar_todos_usuarios(usuarios_db)
            st.session_state.pontos += qtd_pontos_apoio
            st.session_state.pontos_leaderboard_cache = st.session_state.pontos
            atualizar_no_leaderboard(st.session_state.nome_usuario, st.session_state.pontos)
            st.rerun()

        if col_apoio3.button("Rem", key="rem_pontos_apoio", use_container_width=True):
            usuarios_db = carregar_todos_usuarios()
            key_jogador = st.session_state.nome_usuario.lower()
            if key_jogador in usuarios_db:
                usuarios_db[key_jogador]["dados"]["pontos"] = max(0, usuarios_db[key_jogador]["dados"].get("pontos", 0) - qtd_pontos_apoio)
                salvar_todos_usuarios(usuarios_db)
            st.session_state.pontos = max(0, st.session_state.pontos - qtd_pontos_apoio)
            st.session_state.pontos_leaderboard_cache = st.session_state.pontos
            atualizar_no_leaderboard(st.session_state.nome_usuario, st.session_state.pontos)
            st.rerun()

# --- CONTROLE DE MUNDOS ---
st.title("Clicker Game")

if aviso_sistema.strip() != "":
    st.info(f" **Mensagem do ADM:** {aviso_sistema}")

if mult_evento > 1:
    st.warning(f" **EVENTO GLOBAL ATIVO:** Cliques concedendo **{mult_evento}X** de Pontos!")

if mult_sorte > 1:
    st.success(f" **EVENTO DE SORTE ATIVO:** Chances de Pets Raros **{mult_sorte}X**!")

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

# --- CONTEÚDO DOS MUNDOS ---
if st.session_state.mundo_atual == 2:
    st.subheader("Segundo mundo")
    st.info("2X de multiplicador de mundo")
    
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
                st.rerun()

        if st.session_state.pet_slot_m2_2:
            pet = st.session_state.pet_slot_m2_2
            st.write("**Pet Equipado:**")
            try:
                st.image(pet["arquivo"], width=120)
            except Exception:
                st.warning(f"⚠️ Imagem ({pet['arquivo']}) não encontrada.")
            st.caption(f"{pet['nome']} | +{calcular_bonus_pet(pet):,} por clique")

else:
    st.subheader("Primeiro Mundo")
    try:
        st.audio("musica67.mp3")
    except Exception:
        pass

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
        st.write(f"Michael J.: **{ch3_m1_o2:.1f}%** (+100 Pontos) 🍀")
        
        custo_ovo2 = 1000
        desativar_ovo2 = st.session_state.pontos < custo_ovo2 or loja_em_cooldown
        if st.button(f"Abrir Ovo = {custo_ovo2} Pontos", disabled=desativar_ovo2, key="botao_ovo2"):
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

# --- 🌟 LOJA DE TOTENS ---
if "exibir_loja_totens" not in st.session_state:
    st.session_state.exibir_loja_totens = False

if st.button("🛒 Abrir Loja de Totens Místicos", use_container_width=True):
    st.session_state.exibir_loja_totens = not st.session_state.exibir_loja_totens
    st.rerun()

if st.session_state.exibir_loja_totens:
    st.subheader("🛒 Loja de Totens Místicos")
    tempo_restante_segundos = 300 - (int(time.time()) % 300)
    st.caption(f"⏳ Os itens da loja mudam em: **{int(tempo_restante_segundos/60)}m {tempo_restante_segundos%60}s**")

    totens_da_rodada = obter_totens_da_rodada()
    col_tot1, col_tot2, col_tot3 = st.columns(3)
    colunas_totens = [col_tot1, col_tot2, col_tot3]

    for idx, totem in enumerate(totens_da_rodada):
        with colunas_totens[idx]:
            st.markdown(f"##### {totem['nome']}")
            st.write(f"⭐ **Raridade:** {totem['raridade']}")
            st.write(f"⚔️ **Bônus:** {totem['multiplicador']}x Crítico")
            st.write(f"💰 **Custo:** {totem['custo']:,} Pts")
            
            btn_desativado = st.session_state.pontos < totem['custo'] or loja_em_cooldown
            if st.button(f"Comprar Totem", key=f"btn_buy_totem_{idx}", disabled=btn_desativado, use_container_width=True):
                if st.session_state.pontos >= totem['custo']:
                    st.session_state.ultima_compra = time.time()
                    st.session_state.pontos -= totem['custo']
                    st.session_state.totem_equipado = totem
                    atualizar_poder_clique()
                    salvar_progresso_atual()
                    st.rerun()

    if st.button("❌ Fechar Loja", key="btn_fechar_totens", use_container_width=True):
        st.session_state.exibir_loja_totens = False
        st.rerun()

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
        {"qtd": 1000, "custo": 100000}, {"qtd": 2500, "custo": 250000}, {"qtd": 5000, "custo": 500005},
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
                    salvar_progresso_atual()
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
                    salvar_progresso_atual()
                    st.rerun()

if st.session_state.nome_usuario:
    atualizar_no_leaderboard(st.session_state.nome_usuario, st.session_state.pontos)

# --- LOG DE ATUALIZAÇÕES ---
st.markdown("---")
st.subheader("Atualizações:")
st.write("(3.4.1) - Correção do Auto-Clicker em tempo real com sincronização a cada 1 segundo.")

# --- 🏆 TABELA DE CLASSIFICAÇÃO GLOBAL ---
st.markdown("---")
st.subheader("Top Global:")
if os.path.exists(LEADERBOARD_FILE):
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            dados_placar = json.load(f)
        
        usuarios_unicos = {}
        for jogador in dados_placar:
            nome = jogador["Jogador"]
            pontos = jogador.get("Points", jogador.get("Pontos", 0))
            if nome.lower() not in usuarios_unicos or pontos > usuarios_unicos[nome.lower()]["Pontos"]:
                usuarios_unicos[nome.lower()] = {"Jogador": nome, "Pontos": pontos}
        
        placar_final = sorted(usuarios_unicos.values(), key=lambda x: x["Pontos"], reverse=True)[:5]
        
        if placar_final:
            dados_formatados = [{"Jogador": j["Jogador"], "Pontos": f"{j['Pontos']:,}"} for j in placar_final]
            st.table(dados_formatados)
        else:
            st.info("O placar está vazio.")
    except Exception:
        st.info("O placar está vazio.")

# --- RESET DE JOGO ---
st.markdown("---")
if not st.session_state.confirmando_reset:
    if st.button("Resetar Jogo", use_container_width=True):
        st.session_state.confirmando_reset = True
        st.rerun()
else:
    st.warning("⚠️ **Você tem certeza absoluta?** Isso apagará permanentemente todos os seus pontos!")
    col_sim, col_nao = st.columns(2)
    
    with col_sim:
        if st.button("SIM, deletar tudo", type="primary", use_container_width=True):
            remover_jogador_leaderboard(st.session_state.nome_usuario)
            usuarios = carregar_todos_usuarios()
            user_key = st.session_state.nome_usuario.lower()
            if user_key in usuarios:
                usuarios[user_key]["dados"] = {
                    "pontos": 0, "poder_base": 1, "pontos_por_segundo": 0,
                    "pet_slot_1": None, "pet_slot_2": None,
                    "pet_slot_m2_1": None, "pet_slot_m2_2": None, "totem_equipado": None,
                    "ultimo_tick": time.time(), "mundo_2_desbloqueado": False, "mundo_atual": 1,
                    "titulo": ""
                }
                salvar_todos_usuarios(usuarios)
            
            st.components.v1.html(f"""<script>window.parent.postMessage({{type: "REMOVE_ACCOUNT", user: "{user_key}"}}, "*");</script>""", height=0, width=0)
            resetar_estados_jogador_local()
            st.rerun()
            
    with col_nao:
        if st.button("NÃO, voltar ao jogo", use_container_width=True):
            st.session_state.confirmando_reset = False
            st.rerun()
