from langgraph.graph import StateGraph, END
from agentstate import AgentState
from nodes.planner import planner_node
from nodes.developer import developer_node
from nodes.reviewer import human_review_node
# from agents.tester import tester_node
from utils import extrair_especificacoes


# Definição do estado inicial
print("⚙️  Configurando o fluxo de desenvolvimento autônomo...")

file_name = "spec"
initial_state = {
    "specs": extrair_especificacoes(file_name),
    "iterations": 0,
    "max_iterations": 3,
    "source_repository_path": "",
    "history": [],
    "success": False,
    "language": "TypeScript",
    "test_framework": "ts-jest",
    "gen_dir": "gen",
    "src_dir": "C:\\Users\\111967\\Projects\\Estudo\\test"
}
config = {"configurable": {"thread_id": "1"}}


# Definição do fluxo
workflow = StateGraph(AgentState)

## Adicionando os nós
workflow.add_node("planner", planner_node)
workflow.add_node("developer", developer_node)
# workflow.add_node("tester", tester_node)

# Novo Nó: Revisão de Delta
workflow.add_node("reviewer", human_review_node)

## Definindo as conexões
workflow.set_entry_point("planner")
workflow.add_edge("planner", "developer")
# workflow.add_edge("developer", "tester")

## Lógica Condicional (O "Coração" do seu fluxo)
# def route_after_test(state):
#     if state["success"]:
#         return "reviewer"
#     if state["iterations"] >= state["max_iterations"]:
#         return "fail"
#     return "retry"

# workflow.add_conditional_edges(
#     "tester",
#     route_after_test,
#     {
#         "reviewer": "reviewer",
#         "retry": "planner", # Ou volta para o "developer" dependendo da estratégia
#         "fail": END
#     }
# )

## TEMPORÁRIO !!!!!!
workflow.add_edge("developer", "reviewer")
workflow.add_edge("reviewer", END)

app = workflow.compile()


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
    print(resultado_final)