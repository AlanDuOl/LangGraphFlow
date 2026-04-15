import os
import docker
from langchain_ollama import ChatOllama
from agentstate import AgentState


# Agente Tester
# tester_agent = ChatOllama(model="gemma3:27b-cloud", temperature=0)


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


def run_isolated_tests(code_string: str, test_string: str):
    return True, ""
    '''
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
    '''