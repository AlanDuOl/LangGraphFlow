from typing import TypedDict, List, Annotated
import operator

class AgentState(TypedDict):
    objective: str
    plan: str
    code: str
    test_results: str
    iterations: int
    max_iterations: int = 5
    success: bool