from agentstate import AgentState
from utils import persistir_solucao_agente


def persistence_node(state: AgentState):
    print("\n" + "⚙️" * 5 + "  SALVANDO SOLUÇÃO DO AGENTE " + "⚙️" * 5)
    
    arquivosPersistido = persistir_solucao_agente(state)
    
    return {
        "solucao_gerada": arquivosPersistido
        }