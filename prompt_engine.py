import re
from typing import Optional, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from groq import Groq

# ============================================================
# 1. MODOS DA IA (papéis que ela pode assumir)
# ============================================================
MODOS = {
    "tecnico": "Você é um advogado especialista. Use linguagem jurídica precisa e termos técnicos apropriados.",
    "resumido": "Você é um assistente jurídico conciso. Responda em no máximo 3 frases curtas, direto ao ponto.",
    "professor": "Você é um professor de direito. Explique de forma didática, com exemplos e analogias, como se estivesse ensinando um aluno.",
    "detalhado": "Você é um consultor jurídico. Forneça respostas completas, citando artigos de lei, jurisprudência e fundamentações quando cabível.",
    "suporte_tecnico": "Você é um assistente de suporte do sistema. Ajude o usuário com problemas técnicos do bot ou do aplicativo, sem dar informações jurídicas."
}

# ============================================================
# 2. TIPOS DE PROMPTS
# ============================================================
def prompt_simples(pergunta: str, modo: str = "tecnico") -> ChatPromptTemplate:
    """Prompt simples: apenas a pergunta com o papel definido."""
    system = MODOS.get(modo, MODOS["tecnico"])
    return ChatPromptTemplate.from_template(f"{system}\n\nPergunta: {{pergunta}}\nResposta:")

def prompt_estruturado(pergunta: str, modo: str = "tecnico") -> ChatPromptTemplate:
    """Prompt estruturado: resposta com tópicos e formatação."""
    system = MODOS.get(modo, MODOS["tecnico"])
    template = f"""{system}

Responda à pergunta abaixo no seguinte formato:

**Resposta Principal**: (uma frase clara e direta)
**Explicação**: (desenvolvimento, até 3 parágrafos)
**Base Legal**: (se aplicável, cite artigos de lei ou referências)
**Aviso**: (sempre inclua: "Esta é uma orientação inicial. Consulte um advogado para seu caso concreto.")

Pergunta: {{pergunta}}
Resposta:"""
    return ChatPromptTemplate.from_template(template)

def prompt_especializado(pergunta: str, area: str = "civil", modo: str = "tecnico") -> ChatPromptTemplate:
    """Prompt especializado: foco em uma área do direito."""
    areas = {
        "civil": "Direito Civil (contratos, família, responsabilidade civil)",
        "penal": "Direito Penal (crimes, penas, processo penal)",
        "trabalhista": "Direito do Trabalho (CLT, direitos do empregado, rescisão)",
        "consumidor": "Direito do Consumidor (CDC, garantias, vícios)",
        "administrativo": "Direito Administrativo (licitações, servidores, atos administrativos)"
    }
    area_desc = areas.get(area.lower(), "Direito")
    system = MODOS.get(modo, MODOS["tecnico"])
    system += f" Você é especialista em {area_desc}."
    
    template = f"""{system}

Contexto: O usuário está buscando orientação na área de {area_desc}.

Pergunta: {{pergunta}}
Resposta (forneça uma análise focada nesta área):"""
    return ChatPromptTemplate.from_template(template)

# ============================================================
# 3. PROTEÇÕES (filtros de segurança)
# ============================================================
class Protecoes:
    """Classe com métodos estáticos para filtragem e validação."""
    
    # Palavras-chave suspeitas de Prompt Injection
    INJECTION_PATTERNS = [
        r"ignore previous instructions",
        r"ignore all previous commands",
        r"system:\s*override",
        r"you are now",
        r"new system prompt",
        r"\[INST\].*\[/INST\]",  # padrão de injeção em modelos
        r"<\|system\|>.*<\|user\|>",
        r"forget everything",
        r"disregard the above",
        r"you are a different ai",
        r"act as a",
    ]
    
    # Tópicos proibidos (fora do escopo jurídico)
    TOPICOS_PROIBIDOS = [
        r"piratear", r"hackear", r"crack", r"droga", r"explosivo",
        r"pornogr", r"sexo explícito", r"violência gráfica",
        r"como fazer bomba", r"assassinar", r"estuprar",
    ]
    
    @staticmethod
    def validar_pergunta(pergunta: str) -> tuple[bool, str]:
        """
        Retorna (é_valida, mensagem_de_erro).
        Se a pergunta for perigosa, retorna False e o motivo.
        """
        texto = pergunta.lower().strip()
        
        # Verifica injeção
        for pattern in Protecoes.INJECTION_PATTERNS:
            if re.search(pattern, texto):
                return False, "Desculpe, não posso processar essa solicitação. Parece conter instruções maliciosas."
        
        # Verifica tópicos proibidos
        for pattern in Protecoes.TOPICOS_PROIBIDOS:
            if re.search(pattern, texto):
                return False, "Desculpe, esse assunto não está dentro do escopo de atuação deste assistente jurídico."
        
        # Verifica comprimento (evita ataques de buffer)
        if len(pergunta) > 2000:
            return False, "Sua pergunta é muito longa. Por favor, resuma em até 2000 caracteres."
        
        # Verifica se a pergunta parece ser jurídica (palavras-chave mínimas)
        # Se não contiver nenhuma palavra-chave jurídica, pode ser um pedido genérico inadequado
        palavras_juridicas = ["lei", "artigo", "processo", "advogado", "juiz", "tribunal", 
                              "ação", "defesa", "recurso", "contrato", "indenização", "direito"]
        if not any(p in texto for p in palavras_juridicas):
            # Pode ser uma pergunta fora do escopo, mas não bloqueia totalmente
            return True, ""  # apenas aceita, mas o modo vai guiar a resposta
        
        return True, ""
    
    @staticmethod
    def sanitizar_pergunta(pergunta: str) -> str:
        """Remove caracteres suspeitos ou comandos ocultos."""
        # Remove caracteres não-imprimíveis
        pergunta = re.sub(r'[^\x20-\x7E\u00C0-\u00FF]', '', pergunta)
        # Remove múltiplos espaços
        pergunta = re.sub(r'\s+', ' ', pergunta).strip()
        return pergunta

# ============================================================
# 4. GERENCIADOR DE DUAS APIs (Gemini + Groq)
# ============================================================
class DualAIManager:
    """Gerencia duas IAs para comparação e distribuição de tarefas."""
    
    def __init__(self, gemini_api_key: str, groq_api_key: str):
        # Inicializa a IA principal (Gemini) via LangChain
        self.llm_gemini = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=gemini_api_key,
            temperature=0.5,
            max_output_tokens=500
        )
        # Inicializa a segunda IA (Groq) com Llama 3
        self.client_groq = Groq(api_key=groq_api_key)
        self.groq_model = "llama-3.1-8b-instant"
    
    def consultar_gemini(self, prompt_template: ChatPromptTemplate, pergunta: str) -> str:
        """Consulta a IA principal (Gemini)."""
        chain = prompt_template | self.llm_gemini
        resposta = chain.invoke({"pergunta": pergunta})
        return resposta.content
    
    def consultar_groq(self, system_message: str, pergunta: str) -> str:
        """Consulta a IA secundária (Groq/Llama3)."""
        chat_completion = self.client_groq.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": pergunta}
            ],
            model=self.groq_model,
            temperature=0.5,
            max_tokens=500,
        )
        return chat_completion.choices[0].message.content
    
    def comparar_respostas(self, pergunta: str, modo: str = "tecnico",
                           tipo_prompt: str = "simples", area: str = "civil") -> Dict[str, str]:
        """
        Envia a mesma pergunta para ambas as IAs e retorna as duas respostas.
        """
        system_message = MODOS.get(modo, MODOS["tecnico"])
        
        # Gemini (com LangChain e prompt específico)
        if tipo_prompt == "simples":
            template = prompt_simples(pergunta, modo)
        elif tipo_prompt == "estruturado":
            template = prompt_estruturado(pergunta, modo)
        elif tipo_prompt == "especializado":
            template = prompt_especializado(pergunta, area, modo)
        else:
            template = prompt_simples(pergunta, modo)
        
        resposta_gemini = self.consultar_gemini(template, pergunta)
        
        # Groq (com system message e pergunta direta)
        resposta_groq = self.consultar_groq(system_message, pergunta)
        
        return {
            "gemini": resposta_gemini,
            "groq": resposta_groq
        }
    
    def escolher_melhor_resposta(self, pergunta: str, modo: str = "tecnico",
                                 criterio: str = "completude") -> str:
        """
        Compara e escolhe a melhor resposta com base em um critério simples.
        (Para um sistema real, poderia usar um classificador ou análise de sentimento)
        """
        respostas = self.comparar_respostas(pergunta, modo)
        if criterio == "completude":
            # A mais longa tende a ser mais completa
            return respostas["gemini"] if len(respostas["gemini"]) >= len(respostas["groq"]) else respostas["groq"]
        elif criterio == "concisa":
            return respostas["groq"] if len(respostas["groq"]) <= len(respostas["gemini"]) else respostas["gemini"]
        # Padrão: usa Gemini (mais conhecido)
        return respostas["gemini"]
    
    def distribuir_por_area(self, pergunta: str, area: str) -> str:
        """
        Distribui a pergunta para a IA mais adequada à área.
        Exemplo: áreas jurídicas complexas vão para Gemini, consultas rápidas para Groq.
        """
        areas_gemini = ["penal", "administrativo", "tributário"]
        areas_groq = ["civil", "trabalhista", "consumidor"]
        
        if area.lower() in areas_gemini:
            system = MODOS.get("tecnico", "")
            return self.consultar_gemini(prompt_simples(pergunta, "tecnico"), pergunta)
        else:
            system = MODOS.get("tecnico", "")
            return self.consultar_groq(system, pergunta)