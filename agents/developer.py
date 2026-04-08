from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from agentstate import AgentState
from utils import extrair_conteudo_tag

developer_prompt_template = ChatPromptTemplate.from_messages([
    ("system", """Você é um Desenvolvedor Senior especializado em {language}.
Sua tarefa é implementar o código seguindo estritamente o PLANO DE AÇÃO fornecido.
Certifique-se de que sua implementação seja compatível com os testes unitários já criados.
Certifique-se de que sua implementação seja compatível com o stub de código gerado.

REGRAS:
1. Escreva apenas o código funcional.
2. Certifique-se de que o código seja completo e auto-contido.
3. Coloque o código obrigatoriamente entre as tags <code> e </code>.
4. Não inclua explicações fora das tags, apenas o bloco de código.
5. Constantes devem ser sempre UPPER_CASE.
6. Se o plano mencionar um padrão de projeto, implemente-o seguindo as melhores práticas da linguagem."""),
    ("user", "PLANO DE AÇÃO:\n{plan}\n\nTESTES UNITÁRIOS:\n{test_code}\n\nSTUB:\n{stub}")
])

# Agente Developer
developer_agent = ChatOllama(model="qwen3-coder:480b-cloud", temperature=0)

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