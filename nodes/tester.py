import subprocess
import os
import docker
from langchain_ollama import ChatOllama
from agentstate import AgentState


# Agente Tester
# tester_agent = ChatOllama(model="gemma3:27b-cloud", temperature=0)


def tester_node(state: AgentState):
    print("--- [TESTER] EXECUTANDO TESTES NO DOCKER ---")
    
    if not state["solucao_gerada"]:
        print("⚠️  Nenhuma solução gerada para testar. Pulando testes.")
        return state

    # O agente testador poderia gerar os testes aqui, 
    # ou você pode ter testes fixos dependendo do objetivo.
    success, logs = run_isolated_tests_from_folder("gen")

    return {
        "test_results": logs,
        "success": success,
        "iterations": state["iterations"] + 1
    }


def run_isolated_tests_from_folder(source_folder_path: str):
    absolute_folder_path = os.path.abspath(source_folder_path)
    
    if not os.path.exists(absolute_folder_path):
        return False, f"Erro: O diretório {absolute_folder_path} não existe."

    if not prepare_dependencies(absolute_folder_path):
        return False, "Falha ao preparar dependências no host."

    try:
        client = docker.from_env()
        # Docker only needs to run jest now, since node_modules is already in the volume
        command = "npx jest --colors=false"
        
        container_output = client.containers.run(
            image="node:20-slim",
            command=command,
            volumes={absolute_folder_path: {'bind': '/app', 'mode': 'rw'}},
            working_dir="/app",
            network_disabled=True, # Security: No internet needed inside!
            remove=True
        )
        return True, container_output.decode('utf-8')
    
    except docker.errors.ContainerError as e:
        # In Jest, a failing test returns a non-zero exit code, triggering this error
        print(f"Testes falharam com código de saída {e.exit_status}. Logs dos testes:\n{e.stderr.decode('utf-8')}")
        return False, e.stderr.decode('utf-8')
    except Exception as e:
        print(f"Erro inesperado nos testes: {e}")
        return False, str(e)


def prepare_dependencies(folder_path):
    print(f"--- [HOST] Instalando dependências em {folder_path} ---")
    try:
        # shell=True allows using 'cd' and '&&'
        # check=True will raise an error if the command fails
        subprocess.run(
            "npm i", 
            cwd=folder_path, # This is the programmatic way to 'cd gen'
            shell=True, 
            check=True,
            capture_output=True,
            text=True
        )
        print("--- [HOST] Dependências instaladas com sucesso. ---")
        return True
    except subprocess.CalledProcessError as e:
        print(f"--- [ERRO] Falha no npm install: {e.stderr} ---")
        return False