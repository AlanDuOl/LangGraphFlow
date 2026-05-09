from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from agentstate import AgentState
from nodes.planner import planner_node
from nodes.developer import developer_node
from nodes.persistence import persistence_node
from nodes.tester import tester_node
from nodes.reviewer import review_node
from utils import extrair_especificacoes


# Definição do estado inicial
print("⚙️  Configurando o fluxo de desenvolvimento autônomo...")

file_name = "spec"
initial_state = {
    "specs": extrair_especificacoes(file_name),
    "iterations": 0,
    "max_iterations": 2,
    "source_repository_path": "",
    "history": [],
    "success": False,
    "language": "TypeScript",
    "test_framework": "ts-jest",
    "gen_dir": "gen",
    "src_dir": "../Solution/",
    "solucao_gerada": False
}
config = {"configurable": {"thread_id": "1"}}


# Definição do fluxo
workflow = StateGraph(AgentState)

## Adicionando os nós
workflow.add_node("planner", planner_node)
workflow.add_node("developer", developer_node)
workflow.add_node("persistence", persistence_node)
workflow.add_node("tester", tester_node)
workflow.add_node("reviewer", review_node)

## Definindo as conexões
workflow.set_entry_point("planner")
workflow.add_edge("planner", "developer")
workflow.add_edge("developer", "persistence")
workflow.add_edge("persistence", "tester")
workflow.add_edge("tester", "reviewer")
workflow.add_edge("reviewer", END)

## Lógica Condicional (O "Coração" do seu fluxo)
def route_after_test(state):
    # 1. Sucesso total
    if state["success"]:
        return "reviewer"
    
    # 2. Limite de tentativas atingido
    if state["iterations"] >= state["max_iterations"]:
        return "fail"

    # 3. Captura de erros de compilação ou contrato
    logs = state.get("test_results", "")
    
    # Verifica se existe o padrão "error TS" ou outros erros estruturais
    if "error TS" in logs or "ReferenceError" in logs or "Error" in logs:
        print("🚨 Erro de compilação/contrato detectado (TypeScript). Voltando para o PLANNER.")
        return "retry_planner"
    
    # 4. Erros de lógica (ex: o teste rodou mas o valor foi diferente)
    # Nesse caso, tentamos o Developer novamente
    print("⚠️ Falha nos testes de lógica. Tentando correção via DEVELOPER.")
    return "retry_developer"

workflow.add_conditional_edges(
    "tester",
    route_after_test,
    {
        "reviewer": "reviewer",
        "retry_planner": "planner",
        "retry_developer": "developer",
        "fail": END
    }
)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# Execução
print("🚀 Iniciando o fluxo de desenvolvimento autônomo...")
resultado_final = app.invoke(initial_state, config)

# Resultado
print("--- FLUXO FINALIZADO ---")
if resultado_final["success"]:
    print("✅ Código implementado com sucesso!")
    # print(resultado_final)
else:
    print("❌ O fluxo atingiu o limite de tentativas ou falhou.")
    # print(resultado_final)