from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from agentstate import AgentState
from utils import extrair_conteudo_tag

# O Prompt do Planner com as tags que discutimos
planner_prompt_template = ChatPromptTemplate.from_messages([
    ("system", """Você é um Engenheiro de Software Sênior (Reasoning Mode).
Sua tarefa é analisar as ESPECIFICAÇÕES e erros anteriores para criar um plano de ação, um script de testes unitários em {test_framework} 
e um stub (esqueleto) das classes e funções.

Você também deve instruir no plano a criação de arquivos de configuração e gerenciamento de dependencias necessários e criação 
da lógica de UI caso estajam definidos nas especifiações.

DIRETRIZES DE FORMATAÇÃO (OBRIGATÓRIO):
1. Use <analise> para seu raciocínio e <plano> para os passos técnicos.
2. Dentro de <test_code> e <stub>, você deve envolver CADA arquivo em uma tag XML com seu caminho completo.
   Exemplo:
   <tests/engine.test.ts>
   describe('Test', () => {{ ... }});
   </tests/engine.test.ts>
3. PROIBIDO: Não use blocos de código Markdown (```ts). Apenas as tags de caminho.
4. Use Clean Architecture e evite magic numbers.

Linguagem alvo: {language}"""),
    ("user", "ESPECIFICAÇÕES: {specs}\n\nLogs de Erros Anteriores:\n{test_results}")
])

# Agente de Reasoning
planner_agent = ChatOllama(model="gpt-oss:120b-cloud", temperature=0, reasoning=True).with_retry(
    stop_after_attempt=3,  # Tenta até 3 vezes
    wait_exponential_jitter=True # Espera cada vez mais entre as tentativas
)


def planner_node(state: AgentState):
    # 1. Prepara o prompt com os dados que estão no 'state'
    # O LangGraph injeta o dicionário 'state' automaticamente aqui
    prompt_completo = planner_prompt_template.format_messages(
        specs=state["specs"],
        test_results=state.get("test_results", "Nenhum erro ainda."),
        language=state.get("language", "Python"),
        test_framework=state.get("language", "Python"),
    )
    
    # 2. Chama o modelo (Ollama, GPT, etc.)
    print("--- [PLANNER] GERANDO PLANO DE AÇÃO ---")
    response = planner_agent.invoke(prompt_completo)
    
    # 3. Extrai as tags usando aquela função Regex que criamos
    analise = extrair_conteudo_tag(response.content, "analise")
    plano = extrair_conteudo_tag(response.content, "plano")
    test_code = extrair_conteudo_tag(response.content, "test_code")
    stub = extrair_conteudo_tag(response.content, "stub")
    
    # 4. Retorna as atualizações para o estado do grafo
    return {
        "plan": plano,
        "stub": stub,
        "test_code": test_code,
        "history": state["history"] + [f"Análise: {analise}"]
    }