from langgraph.graph import StateGraph, END
from agentstate import AgentState
from agents.planner import planner_node
from utils import extrair_especificacoes, salvar_artefatos
from agents.developer import developer_node
# from agents.tester import tester_node


# Definição do estado inicial
print("⚙️  Configurando o fluxo de desenvolvimento autônomo...")

file_name = "spec"
initial_state = {
    "specs": extrair_especificacoes(file_name),
    "iterations": 0,
    "max_iterations": 3,
    "history": [],
    "success": False,
    "language": "TypeScript",
    "test_framework": "ts-jest"
}
config = {"configurable": {"thread_id": "1"}}


# Definição do fluxo
workflow = StateGraph(AgentState)

## Adicionando os nós
workflow.add_node("planner", planner_node)
workflow.add_node("developer", developer_node)
# workflow.add_node("tester", tester_node)

## Definindo as conexões
workflow.set_entry_point("planner")
workflow.add_edge("planner", "developer")
# workflow.add_edge("developer", "tester")

## Lógica Condicional (O "Coração" do seu fluxo)
def route_after_test(state):
    if state["success"]:
        return "commit"
    if state["iterations"] >= state["max_iterations"]:
        return "fail"
    return "retry"

# workflow.add_conditional_edges(
#     "tester",
#     route_after_test,
#     {
#         "commit": END,
#         "retry": "planner", # Ou volta para o "developer" dependendo da estratégia
#         "fail": END
#     }
# )

app = workflow.compile()


# Execução
print("🚀 Iniciando o fluxo de desenvolvimento autônomo...")
resultado_final = app.invoke(initial_state, config)

# Resultado
print("--- FLUXO FINALIZADO ---")
if resultado_final["code"]:
    salvar_artefatos(resultado_final)
    print("✅ Código implementado com sucesso!")
# if resultado_final["success"]:
#     salvar_artefatos(resultado_final)
#     print("✅ Código implementado com sucesso!")
else:
    print("❌ O fluxo atingiu o limite de tentativas ou falhou.")
    print(resultado_final)