import re
import os
import difflib
from datetime import datetime


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


def salvar_logs(state, output_dir = "fail_logs"):
    # Criar uma pasta para os resultados se não existir
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    code_file = f"solution_log_{timestamp}"
    
    # Salvar o Código Fonte
    if "code" in state and state["code"]:
        with open(f"{output_dir}/{code_file}.py", "w", encoding="utf-8") as f:
            f.write(state["code"])
        print(f"✅ Artefato de código criado em: {output_dir}/{code_file}.py")
    
    test_file = f"test_log_{timestamp}"

    # Salvar o Código de Teste (para você auditar o que a IA testou)
    if "test_code" in state and state["test_code"]:
        with open(f"{output_dir}/{test_file}.py", "w", encoding="utf-8") as f:
            f.write(state["test_code"])
        print(f"✅ Artefato de teste criado em: {output_dir}/{test_file}.py")


def persistir_solucao_agente(state, base_folder="solution"):
    print("\n" + "="*10 + " ⚙️ PERSISTINDO ARTEFATOS " + "="*10)

    # O conteúdo bruto vindo do Developer (contendo os comentários /* path */)
    raw_content = state.get("code", "")
    if not raw_content:
        print("❌ Nenhum código encontrado no estado.")
        salvar_logs(state)
        return

    # 1. Regex melhorado:
    # Procura por /* caminho.extensao */ 
    # O ([\w\/\.\-]+) garante que pegamos apenas caracteres válidos de caminhos
    pattern = r"\/\*\s*([\w\/\.\-]+\.[a-zA-Z0-9]+)\s*\*\/\n(.*?)(?=\/\*|$)"
    matches = re.findall(pattern, raw_content, re.DOTALL)

    if not matches:
        print("⚠️ Formato de arquivo não reconhecido. Verifique as tags /* path */.")
        salvar_logs(state)
        return

    for file_path, file_content in matches:
        file_path = file_path.strip()
        
        # 2. Limpeza de segurança para evitar o OSError
        # Remove quebras de linha ou espaços que a LLM possa ter inserido no nome
        file_path = "".join(c for c in file_path if c not in '\r\n\t*?"<>|')
        
        file_content = file_content.strip()
        
        # 3. Remove tags de Markdown residuais (```ts) caso a LLM tenha falhado
        file_content = re.sub(r"```[a-z]*\n?", "", file_content).replace("```", "").strip()

        # 4. Construção do caminho
        full_path = os.path.join(base_folder, file_path)
        
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(file_content)
            print(f"✅ Arquivo criado: {full_path}")
        except OSError as e:
            print(f"❌ Erro ao criar {full_path}: {e}")

    print("="*35 + "\n")

