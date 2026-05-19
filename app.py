import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime
from database import Database
from prompt_engine import (
    MODOS, prompt_simples, prompt_estruturado, prompt_especializado,
    Protecoes, DualAIManager
)

load_dotenv()

# ========================= CONFIGURAÇÃO INICIAL =========================
st.set_page_config(
    page_title="JurisBot - Assistente Jurídico",
    page_icon="⚖️",
    layout="wide"
)

@st.cache_resource
def init_resources():
    db = Database(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )
    dual_ai = DualAIManager(
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        groq_api_key=os.getenv("GROQ_API_KEY", "")
    )
    return db, dual_ai

db, dual_ai = init_resources()

# Inicializa estado da sessão
if "messages" not in st.session_state:
    st.session_state.messages = []
if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = None
if "atendimento_id" not in st.session_state:
    st.session_state.atendimento_id = None
if "modo_atual" not in st.session_state:
    st.session_state.modo_atual = "professor"
if "tipo_prompt" not in st.session_state:
    st.session_state.tipo_prompt = "estruturado"
if "area_especializada" not in st.session_state:
    st.session_state.area_especializada = "civil"

# ========================= BARRA LATERAL =========================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3444/3444138.png", width=100)
    st.title("⚖️ JurisBot")
    st.markdown("---")

    st.subheader("🎭 Modo de atuação")
    modo = st.selectbox(
        "Escolha o estilo da IA:",
        options=["professor", "tecnico", "resumido", "detalhado", "suporte_tecnico"],
        index=0,
        key="modo_select"
    )
    st.session_state.modo_atual = modo
    st.caption(MODOS[modo][:100] + "...")

    st.markdown("---")

    st.subheader("📝 Tipo de resposta")
    tipo_prompt = st.radio(
        "Formato da resposta:",
        options=["simples", "estruturado", "especializado"],
        index=1,
        key="tipo_prompt_radio"
    )
    st.session_state.tipo_prompt = tipo_prompt

    if tipo_prompt == "especializado":
        st.session_state.area_especializada = st.selectbox(
            "Área do direito:",
            options=["civil", "penal", "trabalhista", "consumidor", "administrativo"]
        )

    st.markdown("---")

    st.subheader("🔍 Comparar IAs")
    usar_comparacao = st.checkbox("Comparar Gemini vs Groq", value=False)

    st.markdown("---")

    st.subheader("👤 Simulação de usuário")
    if st.session_state.usuario_id is None:
        telegram_id = st.number_input("ID Telegram (simulado):", value=123456789)
        nome = st.text_input("Nome:", value="Maria Silva")
        if st.button("Iniciar atendimento"):
            st.session_state.usuario_id = db.inserir_usuario(telegram_id, nome, nome)
            st.session_state.atendimento_id = db.criar_atendimento(st.session_state.usuario_id)
            st.success(f"Atendimento #{st.session_state.atendimento_id} iniciado!")
    else:
        st.success(f"Usuário ID: {st.session_state.usuario_id} | Atendimento: {st.session_state.atendimento_id}")
        if st.button("Encerrar atendimento"):
            st.session_state.messages = []
            st.session_state.usuario_id = None
            st.session_state.atendimento_id = None
            st.rerun()

# ========================= ÁREA PRINCIPAL =========================
st.title("💬 Assistente Jurídico Inteligente")
st.caption("Tire suas dúvidas jurídicas. Lembre-se: isto é uma orientação inicial, não substitui um advogado.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Digite sua pergunta jurídica..."):
    if st.session_state.atendimento_id is None:
        st.error("Por favor, inicie um atendimento na barra lateral primeiro.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        valido, msg_erro = Protecoes.validar_pergunta(prompt)
        if not valido:
            resposta = f"❌ {msg_erro}"
        else:
            with st.spinner("Consultando a IA..."):
                try:
                    if usar_comparacao and os.getenv("GROQ_API_KEY"):
                        respostas = dual_ai.comparar_respostas(
                            prompt, st.session_state.modo_atual,
                            st.session_state.tipo_prompt, st.session_state.area_especializada
                        )
                        resposta = f"**Gemini:** {respostas['gemini']}\n\n---\n**Groq:** {respostas['groq']}\n\n---\n**Melhor resposta:** {dual_ai.escolher_melhor_resposta(prompt, st.session_state.modo_atual)}"
                    else:
                        if st.session_state.tipo_prompt == "simples":
                            template = prompt_simples(prompt, st.session_state.modo_atual)
                        elif st.session_state.tipo_prompt == "estruturado":
                            template = prompt_estruturado(prompt, st.session_state.modo_atual)
                        else:
                            template = prompt_especializado(prompt, st.session_state.area_especializada, st.session_state.modo_atual)
                        resposta = dual_ai.consultar_gemini(template, prompt)
                except Exception as e:
                    resposta = f"Erro ao consultar IA: {str(e)}"

        with st.chat_message("assistant"):
            st.markdown(resposta)
            with st.expander("📄 Texto completo da resposta"):
                st.text(resposta)

        st.session_state.messages.append({"role": "assistant", "content": resposta})
        db.registrar_mensagem(st.session_state.atendimento_id, "usuario", prompt)
        db.registrar_mensagem(st.session_state.atendimento_id, "bot", resposta)