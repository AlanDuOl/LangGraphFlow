from typing import Annotated, TypedDict
import operator

# Função para substituir o valor antigo pelo novo
def replace(old, new):
    return new

class AgentState(TypedDict):
    specs: str
    plan: Annotated[str, replace] # Usa a função de substituição
    code: Annotated[str, replace]
    stub: Annotated[str, replace]
    test_code: Annotated[str, replace]
    test_results: Annotated[str, replace]
    test_framework: str
    language: str
    iterations: Annotated[int, replace]
    max_iterations: int 
    success: Annotated[bool, replace]
    
    # Para o history, operator.add funciona perfeitamente pois recebe (list1, list2)
    history: Annotated[list, operator.add]
    
    gen_dir: str
    src_dir: str
    solucao_gerada: Annotated[bool, replace]