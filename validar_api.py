import os
from dotenv import load_dotenv
from google import genai
from database import Database

# Carrega variáveis de ambiente
load_dotenv()

# DEBUG: Verifica se as variáveis foram carregadas
print("=== DEBUG: Variáveis de ambiente ===")
print("DB_NAME:", os.getenv("DB_NAME"))
print("DB_USER:", os.getenv("DB_USER"))
print("DB_PASSWORD:", repr(os.getenv("DB_PASSWORD")))  # repr mostra espaços extras
print("DB_HOST:", os.getenv("DB_HOST"))
print("DB_PORT:", os.getenv("DB_PORT"))
print("GEMINI_API_KEY:", "OK" if os.getenv("GEMINI_API_KEY") else "NÃO ENCONTRADA")
print("===================================\n")

# Só prossiga se a senha não estiver vazia
if not os.getenv("DB_PASSWORD"):
    print("❌ ERRO: DB_PASSWORD não foi definida. Verifique o arquivo .env.")
    exit(1)

# Configuração da IA e banco de dados
client_ia = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
db = Database(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432")
)

def executar_teste():
    print("=== Teste de Integração: IA + Banco de Dados ===\n")

    usuario_telegram_id = 123456789
    usuario = db.inserir_usuario(
        telegram_id=usuario_telegram_id,
        username="cliente_teste",
        nome="Maria Silva"
    )
    print(f"✅ Usuário criado/recuperado com ID: {usuario}")

    atendimento = db.criar_atendimento(usuario)
    print(f"✅ Atendimento iniciado com ID: {atendimento}")

    pergunta = "Explique em uma frase o que é um contrato de honorários advocatícios."
    print(f"🤖 Enviando pergunta: '{pergunta}'")
    resposta_ia = client_ia.models.generate_content(
        model="gemini-2.5-flash",
        contents=pergunta
    )
    texto_resposta = resposta_ia.text
    print(f"🤖 Resposta da IA: {texto_resposta}")

    db.registrar_mensagem(atendimento, "usuario", pergunta)
    db.registrar_mensagem(atendimento, "bot", texto_resposta)
    print("✅ Mensagens registradas no banco de dados.\n")
    print("=== Teste concluído com sucesso! ===")
    db.fechar()

if __name__ == "__main__":
    executar_teste()