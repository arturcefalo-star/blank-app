import streamlit as st
import time
import random
import json
import os
from streamlit_autorefresh import st_autorefresh

# Arquivos de salvamento
SAVE_FILE = "savegame.json"
LEADERBOARD_FILE = "leaderboard.json"

# --- FUNÇÕES DE ARQUIVO E LÓGICA ---

def salvar_jogo():
    dados = {
        "pontos": st.session_state.pontos,
        "poder_base": st.session_state.poder_base,
        "pontos_por_segundo": st.session_state.pontos_por_segundo,
        "pet_slot_1": st.session_state.pet_slot_1,
        "pet_slot_2": st.session_state.pet_slot_2,
        "ultimo_tick": st.session_state.ultimo_tick,
        "nome_usuario": st.session_state.nome_usuario # Novo salvamento
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
            # Remove duplicatas e limpa
            usuarios_unicos = {}
            for jogador in dados:
                nome = jogador["Jogador"]
                pontos = jogador.get("Pontos", 0)
                if nome.lower() not in usuarios_unicos or pontos > usuarios_unicos[nome.lower()]["Pontos"]:
                    usuarios_unicos[nome.lower()] = {"Jogador": nome, "Pontos": pontos}
            return sorted(usuarios_unicos.values(), key=lambda x: x["Pontos"], reverse=True)[:5]
        except: return []
    return []

# Nova função para remover um nome antigo da tabela
def remover_jogador_leaderboard(nome_antigo):
    leaderboard = carregar_leaderboard()
    # Filtra mantendo apenas quem NÃO é o nome antigo
    novo_leaderboard = [j for j in leaderboard if j["Jogador"].lower() != nome_antigo.lower()]
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(novo_leaderboard, f, ensure_ascii=False, indent=4)

def salvar_no_leaderboard(nome, pontos):
    leaderboard = carregar_leaderboard()
    # Adiciona ou atualiza
    jogador_encontrado = False
    for jogador in leaderboard:
        if jogador["Jogador"].lower() == nome.lower():
            jogador_encontrado = True
            jogador["Pontos"] = pontos # Atualiza a pontuação
            break
    if not jogador_encontrado:
        leaderboard.append({"Jogador": nome, "Pontos": pontos})
        
    leaderboard = sorted(leaderboard, key=lambda x: x["Pontos"], reverse=True)[:5]
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(leaderboard, f, ensure_ascii=False, indent=4)
    return leaderboard

# --- INICIALIZAÇÃO ---
dados_salvos = carregar_jogo() or {}

if "pontos" not in st.session_state:
    st.session_state.pontos = dados_salvos.get("pontos", 0)
    st.session_state.poder_base = dados_salvos.get("poder_base", 1)
    st.session_state.pontos_por_segundo = dados_salvos.get("pontos_por_segundo", 0)
    st.session_state.ultimo_tick = dados_salvos.get("ultimo_tick", time.time())
    st.session_state.nome_usuario = dados_salvos.get("nome_usuario", "") # Nome atual
    st.session_state.pet_slot_1 = dados_salvos.get("pet_slot_1", None)
    st.session_state.pet_slot_2 = dados_salvos.get("pet_slot_2", None)

# [Mantenha aqui as funções auxiliares de poder_clique, autorefresh, etc, como já estavam]
def atualizar_poder_clique():
    bonus = (st.session_state.pet_slot_1["bonus"] if st.session_state.pet_slot_1 else 0) + \
            (st.session_state.pet_slot_2["bonus"] if st.session_state.pet_slot_2 else 0)
    st.session_state.poder_clique = st.session_state.poder_base + bonus

atualizar_poder_clique()

# --- INTERFACE ---
st.title("Clicker Game")

# Botão principal
if st.button("            Click Here          ", use_container_width=True):
    st.session_state.pontos += st.session_state.poder_clique
    salvar_jogo()

st.metric("Pontos Atuais", st.session_state.pontos)
st.markdown("---")

# 7. TABELA DE CLASSIFICAÇÃO COM TROCA DE NOME
st.subheader("🏆 Tabela de Classificação")

# Input que já vem com o nome atual, se houver
nome_input = st.text_input("Digite seu nome para o recorde:", value=st.session_state.nome_usuario, max_chars=15)

if st.button("Enviar Pontuação para o Placar"):
    if nome_input.strip() == "":
        st.warning("Digite um nome válido!")
    else:
        # Lógica de Troca de Nome
        nome_novo = nome_input.strip()
        nome_antigo = st.session_state.nome_usuario
        
        # Se o nome mudou e havia um nome antigo salvo, removemos o antigo da tabela
        if nome_antigo != "" and nome_novo.lower() != nome_antigo.lower():
            remover_jogador_leaderboard(nome_antigo)
            st.success(f"Nome alterado de {nome_antigo} para {nome_novo}!")
        
        # Salva o novo nome e pontuação
        st.session_state.nome_usuario = nome_novo
        salvar_no_leaderboard(nome_novo, st.session_state.pontos)
        salvar_jogo()
        st.rerun()

dados_placar = carregar_leaderboard()
if dados_placar:
    st.table(dados_placar)

# [Mantenha o restante do código, como reset de jogo, etc.]
