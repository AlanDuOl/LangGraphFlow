from langchain_ollama import ChatOllama

# Agente Tester
tester_agent = ChatOllama(model="gemma3:27b-cloud", temperature=0)