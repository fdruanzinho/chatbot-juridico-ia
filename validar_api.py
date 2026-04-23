import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Inicializa o cliente da API Gemini com sua chave
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def validar_conexao_api():
    """
    Função para validar a comunicação com a API do Google Gemini.
    """
    try:
        resposta = client.models.generate_content(
            model="gemini-2.5-flash",  # Modelo atual e funcional
            contents="Explique em uma frase o que é um contrato de honorários advocatícios."
        )
        
        print("✅ Conexão com a API do Gemini estabelecida com sucesso!")
        print(f"🤖 Resposta da IA: {resposta.text}")
        
    except Exception as e:
        print("❌ Falha na conexão com a API do Gemini:")
        print(f"Erro: {e}")
        print("\n🔍 Possíveis soluções:")
        print("- Verifique se a chave da API está correta no arquivo .env.")
        print("- Execute o script `listar_modelos.py` para ver os modelos disponíveis para sua chave.")

if __name__ == "__main__":
    validar_conexao_api()