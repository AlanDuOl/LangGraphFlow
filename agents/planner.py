from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from agentstate import AgentState
from utils import extrair_conteudo_tag

# O Prompt do Planner com as tags que discutimos
planner_prompt_template = ChatPromptTemplate.from_messages([
    ("system", """Você é um Engenheiro de Software Sênior (Reasoning Mode).
Sua tarefa é analisar as ESPECIFICAÇÕES e erros anteriores (quando houver) para criar um plano de ação de implementação do código, 
gerar um script de testes unitários completo usando {test_framework} e um stub (esqueleto do código) das classes e funções a serem criadas 
e usadas nos testes unitários.

Ao elaborar o plano, certifique-se de que a arquitetura siga padrões de projeto consolidados. 
Identifique no plano quais constantes devem ser criadas para evitar valores fixos (magic numbers) no corpo das funções.
Siga os princípios de Clean Architecture, separando a lógica de negócio das dependências externas.

DIRETRIZES:
1. Analise a falha se houver um log de erro.
2. Responda SEMPRE usando as tags <analise> para seu raciocínio e <plano> para os passos.
3. Coloque o código de teste entre as tags <test_code>.
4. Coloque o stub entre as tags <stub>.

Linguagem alvo: {language}"""),
    ("user", "ESPECIFICAÇÕES: {specs}\n\nLogs de Erros Anteriores:\n{test_results}")
])

# Agente de Reasoning
planner_agent = ChatOllama(model="gpt-oss:120b-cloud", temperature=0, reasoning=True)


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


'''
from langchain_core.messages import HumanMessage, SystemMessage


# Criando uma mensagem
mensagem = [
    HumanMessage(content="Explique o que é um ambiente virtual em Python de forma curta.")
]

# Chamada para o modelo
resposta = planner_agent.invoke(mensagem)
print(resposta.content)
'''