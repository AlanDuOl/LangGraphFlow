from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from agentstate import AgentState
from utils import extrair_conteudo_tag

# O Prompt do Planner com as tags que discutimos
planner_prompt_template = ChatPromptTemplate.from_messages([
("system", """Você é um Engenheiro de Software Sênior (Reasoning Mode).
Sua tarefa é analisar as ESPECIFICAÇÕES e possíveis erros para criar um plano de ação, 
um script de testes unitários em {test_framework} e um stub (esqueleto) das classes e funções.

Você também deve instruir no plano a criação de arquivos de configuração e gerenciamento de dependencias necessários e criação 
da lógica de UI, caso estajam definidos nas especifiações.

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
# Adicionamos o histórico de mensagens para manter a memória da conversa se necessário
MessagesPlaceholder(variable_name="history"), 
("user", """
SITUAÇÃO ATUAL:
- Iteração: {iterations} de {max_iterations}
- Especificações: {specs}

RESULTADOS DOS TESTES ANTERIORES:
{test_results}

TAREFA:
Se 'test_results' contiver erros, analise por que o plano anterior falhou e proponha uma correção no <analise> e no <plano>. 
Se for a primeira iteração, crie o plano do zero.
""")
])

# Agente de Reasoning
planner_agent = ChatOllama(
    model="gemma4:31b-cloud", 
    # model="qwen3-next:80b-cloud", 
    # model="gpt-oss:120b-cloud", 
    temperature=0, reasoning=True).with_retry(
    stop_after_attempt=3,  # Tenta até 3 vezes
    wait_exponential_jitter=True # Espera cada vez mais entre as tentativas
)


def planner_node(state: AgentState):
    # 1. Recupera os resultados de teste de forma segura
    erros_atuais = state.get("test_results", "Nenhum erro detectado ainda. Esta é a primeira tentativa.")
    
    # 2. Prepara o prompt
    # O MessagesPlaceholder "history" espera uma lista de objetos BaseMessage
    prompt_completo = planner_prompt_template.format_messages(
        specs=state["specs"],
        test_results=erros_atuais,
        iterations=state.get("iterations", 0),
        max_iterations=state.get("max_iterations", 4),
        language=state.get("language", "TypeScript"),
        test_framework=state.get("test_framework", "ts-jest"),
        history=state.get("history", []) # Passa a lista de mensagens acumulada
    )
    
    print(f"--- [PLANNER] ANALISANDO ITERAÇÃO {state.get('iterations')} ---")
    response = planner_agent.invoke(prompt_completo)
    
    # 3. Extrai as tags usando aquela função Regex que criamos
    analise = extrair_conteudo_tag(response.content, "analise")
    plano = extrair_conteudo_tag(response.content, "plano")
    test_code = extrair_conteudo_tag(response.content, "test_code")
    stub = extrair_conteudo_tag(response.content, "stub")
    
    # 3. Retorno com atualização de histórico
    # Usamos o conteúdo da análise para alimentar a memória do próximo passo
    return {
        "plan": plano,
        "stub": stub,
        "test_code": test_code,
        # Adicionamos a resposta da LLM ao histórico para que o Developer saiba o que mudou
        "history": [response] 
    }