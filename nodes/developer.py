from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from agentstate import AgentState
from utils import extrair_conteudo_tag


developer_prompt_template = ChatPromptTemplate.from_messages([
    ("system", """Você é um Desenvolvedor Senior especializado em {language}.
Sua tarefa é consolidar o PLANO DE AÇÃO, as REFERÊNCIA DE TESTES e a ESTRUTURA DE STUBS em uma implementação COMPLETA.
Garanta que o código final atenda a todas as especificações do PLANO DE AÇÃO, respeite as definições da ESTRUTURA DE STUBS 
e que os testes unitários definidos na REFERÊNCIA DE TESTES passem sem erros.

IMPORTANTE: Os insumos 'REFERÊNCIA DE TESTES' e 'ESTRUTURA DE STUBS' já estão formatados em tags XML de caminho (ex: <path/file.ts>). 
Sua função é usar esses modelos para escrever o código REAL e funcional, mantendo ou refinando essa mesma estrutura de tags.

REGRAS DE FORMATAÇÃO ESTRUTURAL (CRÍTICO):
1. Você deve entregar o resultado final unificado dentro de um par de tags <code> e </code>.
2. Dentro de <code>, envolva cada arquivo (produção e teste) em sua respectiva tag de caminho.
   Exemplo:
   <src/domain/Board.ts>
   export class Board {{ ... }}
   </src/domain/Board.ts>

3. PROIBIDO: Não use blocos de código Markdown (```ts).
4. INTEGRALIDADE: Garanta que o código esteja completo, sem "stubs" ou comentários de "implemente aqui". Todas as chaves de fechamento devem estar dentro das tags.

DIRETRIZES TÉCNICAS:
- Mantenha paridade total com as assinaturas do STUB.
- Adicione nos arquivos de dependências todos os pacotes necessários para que o código não quebre durante a execução.
- Implemente a lógica para que os arquivos passem nos TESTES fornecidos."""),
    ("user", """Gere a implementação final unificada (Código + Testes) baseada nestes insumos:

PLANO DE AÇÃO:
{plan}

REFERÊNCIA DE TESTES (Já em formato de tags):
{test_code}

ESTRUTURA DE STUBS (Já em formato de tags):
{stub}

Lembre-se: O output deve ser apenas o bloco <code> contendo todos os arquivos individuais em suas tags.""")
])

# Agente Developer
# developer_agent = ChatOllama(model="qwen3-coder:480b-cloud", temperature=0).with_retry(
developer_agent = ChatOllama(model="qwen3-coder-next:cloud", temperature=0).with_retry(
    stop_after_attempt=3,  # Tenta até 3 vezes
    wait_exponential_jitter=True # Espera cada vez mais entre as tentativas
)

def developer_node(state: AgentState):
    # 1. Prepara o prompt
    prompt_input = developer_prompt_template.format_messages(
        language=state.get("language", "Python"),
        plan=state["plan"],
        test_code=state["test_code"],
        stub=state["stub"]
    )
    
    # 2. Chama o LLM (Ollama / DeepSeek / Llama)
    print("--- [DEVELOPER] TRADUZINDO PLANO EM CÓDIGO ---")
    response = developer_agent.invoke(prompt_input)
    
    # 3. Extrai o código usando a função Regex que criamos
    generated_code = extrair_conteudo_tag(response.content, "code")
    
    # Se o modelo falhar em usar as tags, uma estratégia de segurança:
    if not generated_code:
        # Tenta pegar o que estiver entre triple backticks (comum em LLMs)
        generated_code = extrair_conteudo_tag(response.content, f"```{state.get("language", "Python")}") or response.content

    # 4. Atualiza o estado
    return {
        "code": generated_code
    }