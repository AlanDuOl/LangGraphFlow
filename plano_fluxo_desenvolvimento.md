
# Implementação fluxo desenvolvimento LangGraph

## Arquitetura do Fluxo

O fluxo será composto por quatro estados principais:
    - Planner (Reasoning): Recebe o requisito e gera o plano de ação.
    - Developer: Recebe o plano e escreve o código.
    - Tester: Executa os testes unitários.
    - Router (Lógica de Controle): Verifica se os testes passaram. Se sim, finaliza; se não, incrementa um contador e volta ao Planner (ou Developer).

## Implementação Sugerida (Conceitual)

Abaixo, apresento como estruturar isso utilizando o LangGraph:

### 1. Definição do Estado

Primeiro, definimos o que o grafo precisa "lembrar" durante a execução.

Exemplo (python):

    from typing import TypedDict, List, Annotated
    import operator

    class AgentState(TypedDict):
        objective: str
        plan: str
        code: str
        test_results: str
        iterations: int
        max_iterations: int
        success: bool

### 2. Os Nós (Agentes)

Cada função abaixo representa um agente especializado.
    - Planner Node: Utiliza um modelo de reasoning (como GPT-4o ou Claude 3.5 Sonnet) para estruturar os passos.
    - Developer Node: Recebe o plan e gera a implementação.
    - Tester Node: Este nó pode ser um agente que escreve testes ou uma ferramenta (Tool) que executa o código em um ambiente seguro e retorna o erro do compilador/pytest.

### 3. A Lógica do Grafo

Exemplo (python):

    from langgraph.graph import StateGraph, END

    workflow = StateGraph(AgentState)

    # Adicionando os nós
    workflow.add_node("planner", planner_agent)
    workflow.add_node("developer", developer_agent)
    workflow.add_node("tester", tester_agent)

    # Definindo as conexões
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "developer")
    workflow.add_edge("developer", "tester")

    # Lógica Condicional (O "Coração" do seu fluxo)
    def route_after_test(state):
        if state["success"]:
            return "commit"
        if state["iterations"] >= state["max_iterations"]:
            return "fail"
        return "retry"

    workflow.add_conditional_edges(
        "tester",
        route_after_test,
        {
            "commit": END,
            "retry": "planner", # Ou volta para o "developer" dependendo da estratégia
            "fail": END
        }
    )

    app = workflow.compile()

## Considerações Importantes para o seu Sucesso

### Onde o "Reasoning" brilha

Para o Agente Planner, recomendo usar prompts que forcem o Chain of Thought. No LangChain, você pode usar o ChatPromptTemplate com instruções sistêmicas rigorosas ou modelos que já possuem essa natureza (como a série O1 da OpenAI).

### A Execução dos Testes

Para o Agente Testador, não confie apenas em LLM "imaginando" se o código funciona. Use o PythonAstREPLTool do LangChain ou uma sandbox (como Docker ou instâncias temporárias) para rodar o código de fato. O feedback do erro real (Stacktrace) é o que faz o Agente Developer corrigir o código com precisão na segunda tentativa.

### Gestão de Erros e Loops Infinitos

Como você mencionou o limite de X vezes, o campo iterations no estado é vital. Sem ele, você pode consumir sua cota de API rapidamente se os agentes entrarem em um conflito lógico onde um quebra o que o outro conserta.

## Implementação com Ollama e LangChain

### 1. Setup com Ollama e LangChain

A integração é direta. Você pode definir cada agente usando o ChatOllama.

    from langchain_ollama import ChatOllama

    # Agente de Reasoning (ex: Llama 3.1 70B se tiver GPU, ou 8B)
    planner_llm = ChatOllama(model="llama3.1:8b", temperature=0)

    # Agente Developer (ex: CodeLlama ou DeepSeek-Coder)
    developer_llm = ChatOllama(model="deepseek-coder-v2", temperature=0)

### 2. A Estrutura do Testador Local

Para o Testador, recomendo não usar apenas LLM. Como você está rodando localmente, você pode usar uma ferramenta de execução real. O LangChain possui o PythonREPLTool, que executa código Python no seu ambiente.

#### O fluxo de correção (Self-Correction)

Quando o teste falha, o segredo é capturar o erro do terminal e passá-lo de volta:
    1. O Agente Testador tenta rodar pytest ou unittest.
    2. Se falhar, ele captura o Traceback do erro.
    3. Esse erro é injetado no estado do Grafo: state['test_results'] = error_message.
    4. O Planner ou o Developer recebe esse erro na próxima iteração e sabe exatamente o que consertar.

### 3. Exemplo de Prompt de "Reasoning" para o Planner

No seu caso, o Planner precisa ser o "cérebro" que mantém a visão geral. Use um prompt estruturado:
    "Você é um Engenheiro de Software Sênior. Sua tarefa é criar um plano técnico detalhado.
    Se houver erros de testes anteriores (histórico abaixo), analise por que falhou antes de propor a nova abordagem.
    Histórico de Erros: {test_results}"

### 4. Dicas para a Transição (Local -> Nuvem)

Para facilitar a migração futura para modelos como GPT-4o ou Claude 3.5 Sonnet, siga estas boas práticas agora:
    - Abstração do Modelo: Use a interface BaseChatModel do LangChain para que a troca de ChatOllama para ChatOpenAI seja apenas a alteração de uma linha de código.
    - LangSmith: Mesmo rodando localmente, ative o LangSmith. Ele permitirá que você veja visualmente o grafo sendo percorrido e onde exatamente o loop de testes está falhando. É um "debugger" visual essencial para LangGraph.
    - Pydantic para Output: Use with_structured_output para garantir que seus agentes locais respondam em JSON. Isso evita que o fluxo quebre porque o modelo local adicionou um comentário desnecessário na resposta.

## Configuração Via Docker

### 1. Instalação

Criar o ambeinte virtual no python:
    python -m venv .venv
Ativar o ambiente:
    .venv\Scripts\activate
Desativa o ambiente:
    deactivate
Verificar se o ambiente virtual está ativo:
    where python
Gerar arquivos com dependencias:
    pip freeze > requirements.txt
Recriar dependencias do ambiente:
    pip install -r requirements.txt

No seu ambiente virtual, instale a biblioteca:
    pip install docker

### 2. Estrutura de Execução Isolada

A ideia é: o Agente Developer salva o código em uma pasta, e o Docker monta essa pasta como um volume.
Script python:
    import docker
    import os

    def run_isolated_tests(code_string: str, test_string: str):
        client = docker.from_env()
        
        # 1. Cria um diretório temporário para o código
        tmp_path = os.path.abspath("./sandbox")
        os.makedirs(tmp_path, exist_ok=True)
        
        with open(f"{tmp_path}/solution.py", "w") as f:
            f.write(code_string)
        with open(f"{tmp_path}/test_code.py", "w") as f:
            f.write(test_string)

        try:
            # 2. Executa o container
            # Usamos 'python:3.11-slim' por ser leve
            container = client.containers.run(
                image="python:3.11-slim",
                command="python3 -m unittest /app/test_code.py",
                volumes={tmp_path: {'bind': '/app', 'mode': 'rw'}},
                working_dir="/app",
                detach=False, # Espera a execução terminar
                stdout=True,
                stderr=True,
                remove=True   # Deleta o container automaticamente após o uso
            )
            return True, container.decode('utf-8')
        
        except docker.errors.ContainerError as e:
            # Se o teste falhar (exit code != 0), o erro cai aqui
            return False, e.stderr.decode('utf-8')
        except Exception as e:
            return False, str(e)

### 3. Integrando no Nó do LangGraph

Agora, veja como isso se encaixa no fluxo que discutimos. O nó de teste não apenas "pensa", ele age.
Script python:
    def tester_node(state: AgentState):
    print("--- EXECUTANDO TESTES NO DOCKER ---")

    # O agente testador poderia gerar os testes aqui, 
    # ou você pode ter testes fixos dependendo do objetivo.
    success, logs = run_isolated_tests(state["code"], state["test_code"])

    return {
        "test_results": logs,
        "success": success,
        "iterations": state["iterations"] + 1
    }

### 4. Vantagens Práticas dessa Configuração

    - Captura de Logs: O e.stderr captura exatamente o que o unittest ou pytest cuspiria no terminal. Esse log é o "ouro" que o seu Agente Developer precisa para corrigir o código.
    - Limpeza Automática: O parâmetro remove=True evita que você termine o dia com 500 containers parados ocupando espaço no seu HD.
    - Timeout (Dica de Ouro): Em implementações reais, é bom adicionar um parâmetro timeout=30 no containers.run. Se o agente gerar um loop infinito (while True), o Docker mata o processo para você.

## O Prompt do Agente de Reasoning (Modo Debugger)

Para que o seu agente Reasoning (Planner) saiba o que fazer com os erros do Docker, você precisará de um prompt que diga:
    "Abaixo está o erro retornado pelo interpretador Python. Analise a Stacktrace e identifique se o erro é de lógica, sintaxe ou falta de dependência."

Quando o fluxo volta por causa de uma falha, o prompt deve mudar ligeiramente de "Planejador" para "Analista de Erros".

Python:
    SYSTEM_PROMPT_PLANNER = """
    Você é um Arquiteto de Software Especialista em Reasoning e Debugging.
    Sua missão é criar ou revisar planos de implementação baseados em requisitos técnicos.

    ### DIRETRIZES:
    1. Analise o objetivo original.
    2. Se houver um erro de execução anterior (fornecido abaixo), identifique a causa raiz:
    - Erro de Sintaxe: O código está mal escrito.
    - Erro de Lógica: O código rodou, mas o resultado foi incorreto.
    - Erro de Ambiente: Faltou uma biblioteca ou permissão.
    3. Proponha um plano de correção passo a passo que evite o erro anterior.
    4. Mantenha o plano conciso e focado na solução técnica.
    """

### 1. Estrutura da Mensagem de Retorno

No LangGraph, quando você detecta que state["success"] == False, você deve formatar a entrada do Planner assim:
    def format_planner_input(state: AgentState):
    history_context = ""
    if state["test_results"]:
        history_context = f"""
        ### FALHA DETECTADA NA TENTATIVA ANTERIOR ###
        CÓDIGO EXECUTADO:
        {state['code']}

        LOG DE ERRO DO DOCKER (Stacktrace):
        {state['test_results']}
        """

    return {
        "role": "user",
        "content": f"Objetivo: {state['objective']}\n{history_context}\n\nPor favor, forneça o plano de ação."
    }

### 2. O Fluxo de Pensamento do Agente Local

Modelos locais (especialmente os de 7B ou 8B parâmetros) podem se perder em textos longos. Para ajudá-los, o Agente de Reasoning deve sempre responder em um formato que o Agente Developer entenda bem.

Exemplo de Resposta Esperada do Planner:
Análise do Erro: O erro IndexError ocorreu porque a lista estava vazia ao tentar acessar o primeiro elemento.
Plano Corrigido:
    - Adicionar uma verificação if not lista: return None.
    - Implementar a lógica de busca garantindo que o retorno seja sempre tipado.
    - Atualizar o script de teste para cobrir o caso de lista vazia.

### 3. Dica de Ouro: "Chain of Thought" Forçado

Se o seu modelo local estiver ignorando o erro do Docker e repetindo o mesmo código, adicione esta instrução ao final do prompt:
    "Antes de apresentar o plano, escreva uma seção chamada 'PENSAMENTO CRÍTICO' onde você explica para si mesmo por que a implementação anterior falhou e o que deve ser mudado obrigatoriamente."
Isso ativa a capacidade de reasoning do modelo (auto-explicação), o que aumenta drasticamente a taxa de sucesso em loops de auto-correção.

## Configuração do modelo do prompt de saída

Exemplo de Prompt de Saída:
    "Sua resposta deve seguir este formato:

    <analise>
    Explique aqui o que causou o erro no Docker.
    </analise>

    <plano>

    Passo um...

    Passo dois...
    </plano>"

### 1. A Função de Extração (Parser)

Esta função busca o conteúdo dentro das tags que definimos. Ela é robusta porque ignora qualquer texto que o LLM coloque fora das marcações.
    import re

    def extract_tag_content(text: str, tag: str) -> str:
        """
        Extrai o conteúdo entre tags XML-like (ex: <plano>conteúdo</plano>).
        """
        pattern = f"<{tag}>(.*?)</{tag}>"
        # re.DOTALL permite que o '.' capture quebras de linha
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

### 2. Implementação no Fluxo do LangGraph

Agora, veja como os dois nós conversam. O Planner gera o texto sujo, e nós limpamos antes de entregar ao Developer.

Nó do Planner (Reasoning):
    def planner_node(state: AgentState):
    # Aqui chamamos o LLM local (Ollama)
    raw_response = planner_llm.invoke(state["prompt"])

    # Extraímos as partes
    analise = extract_tag_content(raw_response.content, "analise")
    plano = extract_tag_content(raw_response.content, "plano")
    
    print(f"\n--- ANÁLISE DO AGENTE ---\n{analise}")
    
    return {
        "plan": plano,
        "history": state["history"] + [f"Analise: {analise}"]
    }

Nó do Developer (Implementação):
    def developer_node(state: AgentState):
    plan = state["plan"]

    # O prompt do Developer foca apenas no que está dentro da tag <plano>
    prompt = f"Implemente o seguinte plano técnico em Python:\n{plan}"
    
    # O Developer também deve responder entre tags (ex: <code>) para facilitar
    raw_response = developer_llm.invoke(prompt)
    code = extract_tag_content(raw_response.content, "code")
    
    return {"code": code}

### 3. Por que isso funciona melhor localmente?

    - Tolerância a "Conversa Fiada": Modelos locais adoram ser educados ("Com certeza, aqui está seu plano..."). O Regex descarta isso e pega apenas o que importa.
    - Debug Visual: Ao imprimir a analise no console, você consegue ver se o modelo está realmente entendendo o erro do Docker ou se está apenas chutando.
    - Substituição Fácil: Se no futuro você mudar para um modelo que suporta JSON nativo, basta trocar a lógica da função extract_tag_content por um json.loads(), mantendo a estrutura do grafo intacta.

### Estrutura Final do Prompt para o Planner

Para garantir que o modelo use as tags, termine o prompt dele assim:
    IMPORTANTE: Sua resposta DEVE conter as tags analise (para seu raciocínio sobre erros anteriores) e plano (para os passos técnicos da implementação). Não pule nenhuma tag.
Com essa estrutura de Tags + Regex + Docker, você tem um pipeline de nível profissional rodando inteiramente na sua máquina.
