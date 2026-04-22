# from typing import TypedDict, List, Annotated
# import operator
from typing import TypedDict

class AgentState(TypedDict):
    specs: str
    plan: str
    code: str
    stub: str
    test_code: str
    test_results: str
    test_framework: str
    language: str
    iterations: int
    max_iterations: int = 3
    success: bool
    history: list
    gen_dir: str
    src_dir: str
    solucao_gerada: bool