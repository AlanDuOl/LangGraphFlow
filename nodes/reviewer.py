import difflib
import os
from agentstate import AgentState
from utils import persistir_solucao_agente


def human_review_node(state: AgentState):
    
    # 1. Persiste o código do estado na pasta
    persistir_solucao_agente(state)

    print("\n" + "⚙️" * 5 + "  MODO DE REVISÃO HUMANA (DELTA) " + "⚙️" * 5)
    state["success"] = True
    return state
'''
    has_changes = False
    files_to_sync = []

    # 2. Varre a pasta 'gen' para comparar com 'src'
    for root, _, files in os.walk("gen"):
        for file in files:
            path_gen = os.path.join(root, file)
            path_src = path_gen.replace("gen", "src", 1)
            
            # Mostra o Delta no terminal
            if os.path.exists(path_src):
                with open(path_src, 'r') as f1, open(path_gen, 'r') as f2:
                    diff = list(difflib.unified_diff(f1.readlines(), f2.readlines()))
                    if diff:
                        print(f"\n📄 Alterações em: {path_src}")
                        for line in diff:
                            if line.startswith('+'): print(f"\033[92m{line}\033[0m", end="")
                            elif line.startswith('-'): print(f"\033[91m{line}\033[0m", end="")
                        has_changes = True
                        files_to_sync.append((path_gen, path_src))
            else:
                print(f"\n🆕 Novo arquivo detectado: {path_src}")
                has_changes = True
                files_to_sync.append((path_gen, path_src))

    if not has_changes:
        print("✅ Nenhum delta detectado entre a geração e o código atual.")
        state["success"] = True
        return state

    # 3. Bloqueia a execução esperando seu input (Ideal para as 15h)
    confirmacao = input("\n🚀 Deseja aplicar os deltas acima na pasta /src? (s/n): ")
    
    if confirmacao.lower() == 's':
        for p_gen, p_src in files_to_sync:
            os.makedirs(os.path.dirname(p_src), exist_ok=True)
            with open(p_gen, 'r') as f_src, open(p_src, 'w') as f_dst:
                f_dst.write(f_src.read())
        print("✔️ Sincronização concluída!")
        state["success"] = True
    else:
        print("❌ Sincronização cancelada pelo usuário.")

    return state
'''