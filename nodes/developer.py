from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from agentstate import AgentState
from utils import extrair_conteudo_tag


developer_prompt_template = ChatPromptTemplate.from_messages([
    ("system", """Você é um Desenvolvedor Senior especializado em {language}.
Sua tarefa é consolidar o Plano, os Testes e os Stubs em uma implementação COMPLETA e funcional.

REGRAS DE OURO PARA ARTEFATOS:
1. Você deve entregar TODOS os arquivos (Código de Produção + Testes + Configurações) dentro de um ÚNICO par de tags <code> e </code>.
2. Cada arquivo individual DEVE começar com o comentário exatamente assim: /* caminho/do/arquivo */
3. Não inclua Markdown (como ```ts) dentro das tags <code>. Apenas texto puro de código.
4. Não inclua explicações ou texto introdutório. O retorno deve ser exclusivamente o bloco <code>.

DIRETRIZES TÉCNICAS:
- Constantes em UPPER_CASE.
- Respeite rigorosamente as assinaturas definidas no STUB para que os TESTES passem.
- Siga as melhores práticas de {language} e os padrões de projeto mencionados no plano."""),
    ("user", """Combine os seguintes elementos em uma estrutura de arquivos completa:

PLANO DE AÇÃO:
{plan}

REFERÊNCIA DE TESTES (Siga estas nomenclaturas):
{test_code}

ESTRUTURA DE STUBS (Siga estas assinaturas):
{stub}

Entregue agora todos os arquivos unificados entre as tags <code> e </code>.""")
])

# Agente Developer
developer_agent = ChatOllama(model="qwen3-coder:480b-cloud", temperature=0).with_retry(
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