import os
import cv2
import pytesseract
from pytesseract import Output
import numpy as np
import re
import unicodedata
import pandas as pd
from ast import literal_eval
from rapidfuzz import fuzz


# Defina o TESSDATA_PREFIX para apontar para o diretório correto (com a pasta tessdata)
os.environ["TESSDATA_PREFIX"] = "/opt/homebrew/share/tessdata"

def ler_base_nomes():
    file_path = "base_normalizada.csv"
    base_nomes = pd.read_csv(file_path)
    
    name_columns = ["Nome",
        # "Turma",
        # "Telefone",
        "Nome1_Nome2",
        "Nome1_Sobrenome",
        "Nome1e2_Sobrenome"
    ]
    
    full_name_options = base_nomes["Nome"].dropna().drop_duplicates().tolist()
    
    all_option_names = []
    for col in name_columns:
        all_option_names.extend(base_nomes[col].dropna().tolist())
    
    all_option_names = [normalize_words(n) for n in all_option_names]
    
    return full_name_options, all_option_names


# |--------------------------------|
# |                                |
# |  FUNÇÕES DE PRÉ-PROCESSAMENTO  |
# |                                |
# |--------------------------------|

def preprocess_image(image_path):
    print("Tentando carregar a imagem de:", image_path)
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Imagem não encontrada ou não pode ser lida: {image_path}")
    # Convertendo para escala de cinza
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Binarização (OTSU)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return thresh

def upscale_image(img, scale_factor=2.0):
    """
    Redimensiona a imagem (upsample) para aumentar a resolução.
    Pode ajudar a LSTM do Tesseract a reconhecer textos pequenos.
    """
    # Obtem as dimensões atuais
    height, width = img.shape[:2]
    # Calcula as novas dimensões
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    # Redimensiona usando INTER_CUBIC (mais indicado para ampliar)
    upscaled = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    return upscaled

def adaptive_threshold(img, method='gaussian', blockSize=11, C=2, invert=False):
    """
    Aplica limiarização adaptativa.
      - method='gaussian' usa ADAPTIVE_THRESH_GAUSSIAN_C
      - method='mean' usa ADAPTIVE_THRESH_MEAN_C
    Se invert=True, inverte o resultado (texto claro em fundo escuro).
    """
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    if method.lower() == 'mean':
        thresh_method = cv2.ADAPTIVE_THRESH_MEAN_C
    else:
        thresh_method = cv2.ADAPTIVE_THRESH_GAUSSIAN_C

    binary = cv2.adaptiveThreshold(
        gray,
        255,
        thresh_method,
        cv2.THRESH_BINARY,
        blockSize,
        C
    )
    # Inverte se solicitado
    if invert:
        binary = cv2.bitwise_not(binary)

    return binary

def morphological_ops(img, operation='open', kernel_size=(2,2), iterations=1):
    """
    Aplica operações morfológicas para remover ruídos ou reforçar o texto.
      - operation pode ser 'erode', 'dilate', 'open', 'close'.
      - kernel_size controla o tamanho do kernel.
    """
    kernel = np.ones(kernel_size, np.uint8)

    if operation == 'erode':
        morphed = cv2.erode(img, kernel, iterations=iterations)
    elif operation == 'dilate':
        morphed = cv2.dilate(img, kernel, iterations=iterations)
    elif operation == 'open':
        # Abertura = erode -> dilate (remove ruídos pequenos)
        morphed = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel, iterations=iterations)
    elif operation == 'close':
        # Fechamento = dilate -> erode (une regiões próximas)
        morphed = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel, iterations=iterations)
    else:
        morphed = img  # se não reconhecer a operação, retorna original

    return morphed

def deskew_image(img):
    """
    Tenta corrigir inclinação (deskew) usando OpenCV.
    Funciona melhor se a imagem tiver texto predominantemente horizontal.
    """
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    # Inverte se necessário (texto escuro em fundo claro)
    # Se o texto for claro em fundo escuro, pode-se inverter antes
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    # Obter coordenadas dos contornos
    coords = np.column_stack(np.where(thresh > 0))
    # minAreaRect retorna (centro, (width, height), angulo)
    rect = cv2.minAreaRect(coords)
    angle = rect[-1]

    # Ajuste de ângulo (minAreaRect pode retornar valores como -90 < angle <= 0)
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Rotacionar
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated

# |--------------------------------|


def ocr_with_confidence_filter(image_path, min_confidence=50):
    preprocessed_img = preprocess_image(image_path)
    
    # 1) Upscale
    img_upscaled = upscale_image(preprocessed_img, scale_factor=2.0)

    # 2) Binarização adaptativa
    img_thresh = adaptive_threshold(img_upscaled, method='gaussian', blockSize=11, C=2, invert=False)

    # 3) Operações morfológicas
    img_morph = morphological_ops(img_thresh, operation='open', kernel_size=(2,2), iterations=1)

    # 4) Deskew (se precisar corrigir inclinação)
    img_deskewed = deskew_image(img_morph)

    
    config = r"--oem 3 --psm 6 -l por" 
    
    data = pytesseract.image_to_data(preprocessed_img, config=config, output_type=Output.DICT)
    
    # data = pytesseract.image_to_data(img_upscaled, config=config, output_type=Output.DICT)
    # data = pytesseract.image_to_data(img_thresh, config=config, output_type=Output.DICT)
    # data = pytesseract.image_to_data(img_morph, config=config, output_type=Output.DICT)
    # data = pytesseract.image_to_data(img_deskewed, config=config, output_type=Output.DICT)
    
    linhas = {}    # Agrupa palavras por linha
    
    n = len(data['text'])
    for i in range(n):
        text = data['text'][i]
        try:
            conf = float(data['conf'][i])
        except:
            conf = 0
        line_num = data['line_num'][i]
        
        if conf > min_confidence and text.strip():
            if line_num not in linhas:
                linhas[line_num] = []
            linhas[line_num].append(text)
    texto_filtrado = []
    for line_id in sorted(linhas.keys()):
        texto_filtrado.append(" ".join(linhas[line_id]))
    return "\n".join(texto_filtrado)

def normalize(text):
    text_normalized = unicodedata.normalize('NFD', text.lower())
    text_without_accents = text_normalized.encode('ascii', 'ignore').decode('utf-8')
    return re.sub(r'\W+', '', text_without_accents)

def normalize_words(word):
    if pd.isnull(word):
        return ""
    else :
        words = word.split()
        words = [normalize(word) for word in words]
        return ' '.join(words)

def remover_linhas_extras(texto: str) -> list:
    ignore_substrings = [
        "campus",
        "cta",
        "12228",
        "são josé dos campos",
        "sao jose dos campos",
        "sao jose", 
        "bloco", 
        "predio", 
        "apt", 
        "ap",
        "sjc",
        "rua h8",
        "rua h", 
        "recebedor",
        "destinatario",
        "ida", 
        "assinatura",
        "complemento", 
        "compl", 
        "admin", 
        "entrega", 
        "novo", 
    ]
    linhas = texto.split('\n')
    filtradas = []
    for linha in linhas:
        linha_lower = normalize_words(linha.lower())
        if any(sub in linha_lower for sub in ignore_substrings):
            continue
        filtradas.append(linha.strip())
    return [normalize_words(l).strip() for l in filtradas if l]

def remover_linhas_extras_menos_rigor(texto: str) -> list:
    ignore_substrings = [
        "campus",
        "rua h"
        "12228",
        "são jos", 
        "são josé dos campos",
        "sao jose dos campos"
    ]
    linhas = texto.split('\n')
    filtradas = []
    for linha in linhas:
        norm_line = normalize_words(linha)
        if any(normalize_words(sub) in norm_line for sub in ignore_substrings):
            continue
        filtradas.append(linha.strip())
    return [l for l in filtradas if l]

def is_possible_name(linha: str) -> bool:
    palavras = linha.split()
    if any(any(char.isdigit() for char in p) for p in palavras):
        return False
    if any(any(not char.isalnum() for char in p) for p in palavras):
        return False
    if len(palavras) < 2:
        return False
    if any("sao" in normalize(p) for p in palavras):
        return False
    
    # uppercase_start_count = sum(1 for p in palavras if p and p[0].isupper())
    # if uppercase_start_count <= len(palavras) / 2:
        return False
    
    return True

def match_name_in_list(line_ocr: str, names: list, threshold: int = 99) -> list:
    """
    Verifica, por fuzzy matching, quais nomes da lista 'names' correspondem ao texto 'line_ocr'.
    
    Parâmetros:
        - line_ocr: Texto extraído via OCR.
        - names: Lista de nomes possíveis.
        - threshold: Valor mínimo de similaridade (0-100) para considerar uma correspondência. Default: 70.
    
    Retorna:
        Uma lista com os nomes que tiveram correspondência (similaridade >= threshold).
    """
    line_norm = normalize(line_ocr)
    matched_names = []
    for name in names:
        name_norm = normalize(name)
        similarity = fuzz.partial_ratio(name_norm, line_norm)
        if similarity >= threshold:
            matched_names.append(name)
    return matched_names

def most_likely_name(nome_lido: str, nomes_possiveis: list, threshold: int = 80) -> str:
    """
    Retorna o nome mais provável de uma lista de nomes possíveis, baseado em fuzzy matching.
    """
    nome_lido_norm = normalize(nome_lido)
    best_match = ""
    best_similarity = 0
    for nome in nomes_possiveis:
        nome_norm = normalize(nome)
        similarity = fuzz.partial_ratio(nome_norm, nome_lido_norm)
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = nome
    return best_match

def most_likely_name(nomes_lidos: list, nomes_possiveis: list, threshold: int = 80) -> str:
    """
    Retorna o nome mais provável de uma lista de nomes possíveis, baseado em fuzzy matching.
    """
    best_match = ""
    for nome_lido in nomes_lidos:
        nome_lido_norm = normalize(nome_lido)
        best_similarity = 0
        for nome in nomes_possiveis:
            nome_norm = normalize(nome)
            similarity = fuzz.partial_ratio(nome_norm, nome_lido_norm)
            if similarity < threshold:
                continue
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = nome
    return best_match

def extrair_nome_destinatario_v1(texto: str) -> str:
    linhas_filtradas = remover_linhas_extras(texto)
    # print("\n\nTentativa 1\n\nLinhas filtradas:\n\t", "\n\t".join(linhas_filtradas))
    
    nomes_possiveis = []
    nomes_encontrados_na_base = []
    for linha in linhas_filtradas:
        # se tiver até palavras, não é um nome
        if len(linha.split()) <= 2:
            continue
        
        if match_name_in_list(linha, base_nomes_e_variacoes):
            # print("Nome encontrado na base:", linha)
            # print("Nomes possíveis:", match_name_in_list(linha, base_nomes_e_variacoes))
            nomes_encontrados_na_base.append(linha)
            nomes_possiveis.append(linha)
            
        elif is_possible_name(linha):
            nomes_possiveis.append(linha)
            
    if len(nomes_encontrados_na_base) > 0:
        return nomes_encontrados_na_base
    else:
        return nomes_possiveis


def extrair_nome_destinatario_v2(texto: str) -> str:
    linhas_filtradas = remover_linhas_extras_menos_rigor(texto)
    print("\n\nTentativa 2\n\nLinhas filtradas:\n\t", "\n\t".join(linhas_filtradas))
    
    linhas_possiveis = []
    for linha in linhas_filtradas:
        if is_possible_name(linha):
            linhas_possiveis.append(linha)
    if len(linhas_possiveis) == 1:
        return linhas_possiveis[0]
    else: 
        return "nomes possíveis: " + str(linhas_possiveis)


def tentativas_extracao(texto_cru: str):
    # Tentativa 1: Filtro rigoroso
    nome_dest = extrair_nome_destinatario_v1(texto_cru)
    # print("\n\t\tEU ENCONTTEI AQUI: ", nome_dest)
    
    if not not nome_dest:
        if len(nome_dest) == 1:
            nome_dest = nome_dest[0]
            nome_mais_provavel = most_likely_name(nome_dest, base_nomes_completos)
            print("O mais provavel é ", nome_mais_provavel)
            
        else:
            print("\nForam encontradas múltiplas opções para o destinatário:")
            
            nome_mais_provavel = most_likely_name(nome_dest, base_nomes_completos)
            
            # posicao_mais_provavel = nome_dest.index(nome_mais_provavel)
            print("O mais provavel é ", nome_mais_provavel)
            # print("Sua posição é ", posicao_mais_provavel)
            
            print("Escolha uma das opções abaixo ou insira manualmente:")
            
            for i, option in enumerate(nome_dest):
                print(f"  {i+1}: {option}")
            print("999: Nenhuma das opções")
            user_choice = input("\nDigite o número da opção correta ou pressione ENTER para inserir manualmente: ")
            if user_choice.strip() == "":
                nome_dest = input("Digite manualmente o nome do destinatário: ")
            elif user_choice.strip() == "999": 
                # Continua com outro método
                nome_dest = ""
            else:
                try:
                    idx = int(user_choice.strip()) - 1
                    if 0 <= idx < len(nome_dest):
                        nome_dest = nome_dest[idx]
                    else:
                        nome_dest = input("Opção inválida. Digite manualmente o nome do destinatário: ")
                except:
                    nome_dest = input("Entrada inválida. Digite manualmente o nome do destinatário: ")
            
    else:
        # Se a tentativa 1 não retornou nada, tenta a tentativa 2
        nome_dest = extrair_nome_destinatario_v2(texto_cru)
        if not nome_dest:
            nome_dest = input("Não foi possível extrair o nome automaticamente. Por favor, insira manualmente: ")
    
    return nome_dest


if __name__ == "__main__":
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    base_nomes_completos, base_nomes_e_variacoes = ler_base_nomes()
    
    images_folder = "images" # Pasta com as imagens a serem processadas
    destinatarios = {}  # Armazena os destinatários extraídos
    
    # file_debug = "exemplo_etiqueta4.jpeg"
    # file_debug = "WhatsApp Image 2025-03-06 at 10.16.49.jpeg"
    file_debug = "Debug4.png"
    
    for file_name in os.listdir(images_folder):
        
        # REMOVER SE NAO FOR PARA DEBUGAR
        if file_name != file_debug:
            continue
        
        
        if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(images_folder, file_name)
            
            print(f"\n=== OCR para {file_name} ===")
            try:
                texto_cru = ocr_with_confidence_filter(image_path, 10)
                print("Texto OCR Filtrado:\n", texto_cru)
                
                nome_dest = tentativas_extracao(texto_cru)
                
                if nome_dest:
                    print("\nDestinatário extraído:", nome_dest)
                    destinatarios[file_name] = [nome_dest, most_likely_name(nome_dest, base_nomes_e_variacoes)]
                else:
                    print("\nNenhum destinatário extraído.")
                    destinatarios[file_name] = ["Nenhum destinatário extraído.", np.nan]
                
            except Exception as e:
                print("\nErro:", e)
    
    # Exibe os destinatários em um DataFrame e converte para Markdown
    df = pd.DataFrame([(k, v[0], v[1]) for k, v in destinatarios.items()], columns=["Imagem", "Destinatário Lido", "Destinatário Base"])
    print("\n\n--- Destinatários Extraídos ---")
    print(df.to_markdown(index=False))
    print("\n\n")
