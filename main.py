from langgraph.graph import StateGraph, END
from agentstate import AgentState
from agents.planner import planner_agent
from agents.developer import developer_agent
from agents.tester import tester_agent
from langchain_core.messages import HumanMessage

# Criando uma mensagem
mensagem = [
    HumanMessage(content="Explique o que é um ambiente virtual em Python de forma curta.")
]

# Chamada para o modelo
resposta = planner_agent.invoke(mensagem)

print(resposta.content)

"""
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
"""