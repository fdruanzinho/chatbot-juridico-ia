import os
from dotenv import load_dotenv

# --- ALTERAÇÃO: troca da biblioteca google.genai pelo LangChain ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from database import Database

# Carrega as variáveis de ambiente
load_dotenv()

# ========================= DEBUG =========================
print("=== DEBUG: Variáveis de ambiente ===")
print("DB_NAME:", os.getenv("DB_NAME"))
print("DB_USER:", os.getenv("DB_USER"))
print("DB_PASSWORD:", repr(os.getenv("DB_PASSWORD")))
print("DB_HOST:", os.getenv("DB_HOST"))
print("DB_PORT:", os.getenv("DB_PORT"))

# --- ALTERAÇÃO: variável da API renomeada para seguir padrão do LangChain ---
google_api_key = os.getenv("GEMINI_API_KEY")  # ou GOOGLE_API_KEY se preferir
print("GEMINI_API_KEY:", "OK" if google_api_key else "NÃO ENCONTRADA")
print("===================================\n")

if not os.getenv("DB_PASSWORD"):
    print("❌ ERRO: DB_PASSWORD não foi definida. Verifique o arquivo .env.")
    exit(1)

if not google_api_key:
    print("❌ ERRO: GEMINI_API_KEY não foi definida. Verifique o arquivo .env.")
    exit(1)

# --- ALTERAÇÃO: inicialização do modelo via LangChain ---
# Substitui a linha: client_ia = genai.Client(api_key=...)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=google_api_key,
    temperature=0.5,
    max_output_tokens=800,
)

prompt_template = ChatPromptTemplate.from_template(
    """Você é um assistente jurídico especializado em triagem de casos.

Responda de forma clara e objetiva à pergunta abaixo, em uma única frase completa que termine com ponto final. Não interrompa antes do ponto.

Pergunta: {pergunta}

Resposta:"""
)
# --- ALTERAÇÃO: criação de um prompt template jurídico ---
# Agora usamos um template reutilizável, que pode ser expandido com histórico e contexto.
prompt_template = ChatPromptTemplate.from_template(
    """Você é um assistente jurídico especializado em triagem de casos.

Responda de forma clara e objetiva a seguinte pergunta:

Pergunta: {pergunta}

Resposta:"""
)

# --- ALTERAÇÃO: criação da chain (encadeamento prompt + modelo) ---
chain = prompt_template | llm

# Conexão com o banco de dados (mantida igual)
db = Database(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432")
)

def executar_teste():
    print("=== Teste de Integração: IA (LangChain) + Banco de Dados ===\n")

    # 1. Simular usuário do Telegram
    usuario_telegram_id = 123456789
    usuario = db.inserir_usuario(
        telegram_id=usuario_telegram_id,
        username="cliente_teste",
        nome="Maria Silva"
    )
    print(f"✅ Usuário criado/recuperado com ID: {usuario}")

    # 2. Criar atendimento
    atendimento = db.criar_atendimento(usuario)
    print(f"✅ Atendimento iniciado com ID: {atendimento}")

    # 3. Pergunta de teste
    pergunta = "Explique em uma frase o que é um contrato de honorários advocatícios."
    print(f"🤖 Enviando pergunta: '{pergunta}'")

    # --- ALTERAÇÃO: chamada da IA agora via chain.invoke() ---
    resposta_ia = chain.invoke({"pergunta": pergunta})
    texto_resposta = resposta_ia.content   # extrai o texto

    print(f"🤖 Resposta da IA: {texto_resposta}")

    # 4. Registrar mensagens no banco
    db.registrar_mensagem(atendimento, "usuario", pergunta)
    db.registrar_mensagem(atendimento, "bot", texto_resposta)
    print("✅ Mensagens registradas no banco de dados.\n")
    print("=== Teste concluído com sucesso! ===")
    db.fechar()

if __name__ == "__main__":
    executar_teste()