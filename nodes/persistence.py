from agentstate import AgentState
from utils import persistir_solucao_agente, excluir_solucao_agente


def persistence_node(state: AgentState):
    print("\n" + "⚙️" * 5 + "  SALVANDO SOLUÇÃO DO AGENTE " + "⚙️" * 5)

    # --- Excluir solução anterior ---
    arquivosPersistido = excluir_solucao_agente(state, state['gen_dir'])
    
    if arquivosPersistido:
        arquivosPersistido = persistir_solucao_agente(state, state['gen_dir'])
    
    return {
        "solucao_gerada": arquivosPersistido
        }