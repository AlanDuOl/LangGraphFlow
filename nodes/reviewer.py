import os
import difflib
import shutil
from agentstate import AgentState
from utils import persistir_solucao_agente


def review_node(state: AgentState):
    # Verifica se os testes passaram antes de persistir os arquivos
    if not state["pass_tests"]:
        return state
    
    # CRITICAL: O estado PRECISA ser persistido em 'gen' antes da comparação
    # Se você não persistir, o loop abaixo lerá o que já estava lá, não o que o agente acabou de fazer.
    persistir_solucao_agente(state)

    print("\n" + "⚙️" * 5 + "  MODO DE REVISÃO HUMANA (DELTA) " + "⚙️" * 5)
    
    has_changes = False
    files_to_sync = []

    # Caminhos absolutos para evitar erros de replace
    gen_base = os.path.abspath(state["gen_dir"])
    src_base = os.path.abspath(state["src_dir"])

    for root, _, files in os.walk(gen_base):
        for file in files:
            path_gen = os.path.join(root, file)
            # Calcula o caminho relativo para replicar em 'src'
            rel_path = os.path.relpath(path_gen, gen_base)
            path_src = os.path.join(src_base, rel_path)
            
            if os.path.exists(path_src):
                with open(path_src, 'r', encoding='utf-8') as f1, \
                     open(path_gen, 'r', encoding='utf-8') as f2:
                    
                    # strip() ajuda a ignorar diferenças de apenas uma linha vazia no fim
                    lines_src = f1.readlines()
                    lines_gen = f2.readlines()
                    
                    diff = list(difflib.unified_diff(
                        lines_src, lines_gen, 
                        fromfile=f'src/{rel_path}', 
                        tofile=f'src/{rel_path}',
                        lineterm=''
                    ))

                    if diff:
                        # O diff traz metadados nas primeiras 2-3 linhas, 
                        # verificamos se há conteúdo real além dos headers
                        print(f"\n📄 Alterações em: {rel_path}")
                        for line in diff:
                            if line.startswith('+') and not line.startswith('+++'):
                                print(f"\033[92m{line}\033[0m") # Verde
                            elif line.startswith('-') and not line.startswith('---'):
                                print(f"\033[91m{line}\033[0m") # Vermelho
                            elif line.startswith('@@'):
                                print(f"\033[36m{line}\033[0m") # Ciano (Header do bloco)
                        
                        has_changes = True
                        files_to_sync.append((path_gen, path_src))
            else:
                print(f"\n🆕 Novo arquivo detectado: {rel_path}")
                has_changes = True
                files_to_sync.append((path_gen, path_src))

    if not has_changes:
        print("✅ Nenhum delta detectado entre a geração e o código atual.")
        state["success"] = True
        return state

    confirmacao = input("\n🚀 Deseja aplicar os deltas acima na pasta /src? (s/n): ")
    
    if confirmacao.lower() == 's':
        for p_gen, p_src in files_to_sync:
            os.makedirs(os.path.dirname(p_src), exist_ok=True)
            # Usar shutil ou escrita direta
            with open(p_gen, 'r', encoding='utf-8') as f_gen:
                content = f_gen.read()
                with open(p_src, 'w', encoding='utf-8') as f_src:
                    f_src.write(content)
        print("✔️  Sincronização concluída!")
        
        # --- Excluir solução gerada ---
        print(f"🧹 Removendo arquivos temporários em: {state['gen_dir']}...")
        try:
            shutil.rmtree(gen_base)
            # Opcional: Recriar a pasta vazia se os nós anteriores esperarem que ela exista
            # os.makedirs(gen_base, exist_ok=True)
        except Exception as e:
            print(f"⚠️ Erro ao limpar pasta gen: {e}")
            
        state["success"] = True
    else:
        print("❌ Sincronização cancelada. O estado 'success' permanece False.")
        state["success"] = False # Importante para o LangGraph decidir o próximo passo

    return state