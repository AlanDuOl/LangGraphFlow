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


def persistir_solucao_agente(state, base_folder="gen"):
    print("\n" + "="*10 + " ⚙️ PERSISTINDO ARTEFATOS " + "="*10)

    # REMOVEMOS O 'STUB' DAQUI. 
    # Agora só salvamos o que é código final ou teste real.
    keys_to_scan = ["code", "test_code"] 
    files_count = 0

    for key in keys_to_scan:
        raw_content = state.get(key, "")
        if not raw_content:
            continue
            
        pattern = r"<([^>]+)>(.*?)</\1>"
        matches = re.findall(pattern, raw_content, re.DOTALL)

        for file_tag, file_content in matches:
            # Proteção extra: ignorar tags estruturais
            if file_tag.lower() in ["code", "test_code", "stub", "analise", "plano"]:
                continue

            # Sanitização do caminho (Path)
            file_path = file_tag.strip()
            file_path = "".join(c for c in file_path if c not in '\r\n\t*?"<>|').strip()
            
            # Limpeza do conteúdo (Código)
            content = file_content.strip()
            # Remove qualquer Markdown acidental
            content = re.sub(r"```[a-z]*\n?", "", content).replace("```", "").strip()

            full_path = os.path.join(base_folder, file_path)
            
            try:
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
                
                # Feedback visual de sucesso
                indicator = "✓" if content.endswith(('}', ';', '>')) else "!"
                print(f"✅ [{key.upper()}] {indicator} Salvo: {file_path}")
                files_count += 1
            except Exception as e:
                print(f"❌ Erro ao salvar {file_path}: {e}")

    if files_count == 0:
        print("⚠️ Atenção: Nenhum arquivo detectado nas tags XML.")
    else:
        print(f"\n🚀 Sucesso: {files_count} arquivos sincronizados no disco.")
    
    print("="*35 + "\n")