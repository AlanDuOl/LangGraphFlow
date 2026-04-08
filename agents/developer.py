from langchain_ollama import ChatOllama

# Agente Developer
developer_agent = ChatOllama(model="qwen3-coder:480b-cloud", temperature=0)