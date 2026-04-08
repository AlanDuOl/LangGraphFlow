import re
import os

def extrair_conteudo_tag(text: str, tag: str) -> str:
    """
    Extrai o conteúdo entre tags XML-like (ex: <plano>conteúdo</plano>).
    """
    pattern = f"<{tag}>(.*?)</{tag}>"
    # re.DOTALL permite que o '.' capture quebras de linha
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def extrair_especificacoes(file_name: str) -> str:
    """
    Extrai o conteúdo do arquivo de especificações.
    """
    with open(f"./specs/{file_name}.md", "r", encoding="utf-8") as f:
        return f.read()


def salvar_artefatos(state):
    # Criar uma pasta para os resultados se não existir
    output_dir = "solutions"
    os.makedirs(output_dir, exist_ok=True)
    
    # Salvar o Código Fonte
    if "code" in state and state["code"]:
        with open(f"{output_dir}/solution.py", "w", encoding="utf-8") as f:
            f.write(state["code"])
        print(f"✅ Artefato de código criado em: {output_dir}/solution.py")
    
    # Salvar o Código de Teste (para você auditar o que a IA testou)
    if "test_code" in state and state["test_code"]:
        with open(f"{output_dir}/test_solution.py", "w", encoding="utf-8") as f:
            f.write(state["test_code"])
        print(f"✅ Artefato de teste criado em: {output_dir}/test_solution.py")

