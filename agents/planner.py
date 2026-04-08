from langchain_ollama import ChatOllama

prompt = '''
Você é um Engenheiro de Software Sênior. Sua tarefa é criar um plano técnico detalhado a partir do arquivo de especificações fornecido.
Se houver erros de testes anteriores (histórico abaixo), analise por que falhou antes de propor a nova abordagem.
Histórico de Erros: {test_results}
'''

# Agente de Reasoning
planner_agent = ChatOllama(model="gpt-oss:120b-cloud", temperature=0, reasoning=True)