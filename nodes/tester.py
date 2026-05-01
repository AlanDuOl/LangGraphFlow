import os
import docker
from langchain_ollama import ChatOllama
from agentstate import AgentState


# Agente Tester
# tester_agent = ChatOllama(model="gemma3:27b-cloud", temperature=0)


def tester_node(state: AgentState):
    print("--- [TESTER] EXECUTANDO TESTES NO DOCKER ---")
    
    if not state["solucao_gerada"]:
        return state

    # O agente testador poderia gerar os testes aqui, 
    # ou você pode ter testes fixos dependendo do objetivo.
    success, logs = run_isolated_tests_from_folder("gen")
    
    if not success:
        print(f"Erro nos testes: {logs}")

    return {
        "test_results": logs,
        "success": success,
        "iterations": state["iterations"] + 1
    }


def run_isolated_tests_from_folder(source_folder_path: str):
    
    try:
        client = docker.from_env()
        print("Conectado com sucesso:", client.version())
    except Exception as e:
        print("Falha na conexão:", e)
    
    # 1. Garante que o caminho seja absoluto para o Docker mapear corretamente
    absolute_folder_path = os.path.abspath(source_folder_path)
    
    if not os.path.exists(absolute_folder_path):
        return False, f"Erro: O diretório {absolute_folder_path} não existe."

    try:
        # 2. Executa o container
        # Montamos a pasta inteira dentro de /app no container
        container_output = client.containers.run(
            image="node:20-slim", # Imagem com Node.js
            # Comando para instalar dependências e rodar o jest
            command='sh -c "npm install && npx jest"', 
            volumes={
                absolute_folder_path: {'bind': '/app', 'mode': 'rw'}
            },
            working_dir="/app",
            detach=False,
            stdout=True,
            stderr=True,
            remove=True
        )
        return True, container_output.decode('utf-8')
    
    except docker.errors.ContainerError as e:
        return False, e.stderr.decode('utf-8')
    except Exception as e:
        return False, str(e)