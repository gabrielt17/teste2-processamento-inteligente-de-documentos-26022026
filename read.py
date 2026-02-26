# Desenvolva aqui sua atividade
'''
Este programa extrai o texto de uma fatura
utilizando OCR. Os dados são salvos e então
são feitos alguns cálculos com uma saída formatada.
'''

import easyocr
import matplotlib.pyplot as plt
import cv2
import re

# Função para carregar a imagem em uma matriz do OpenCV
def open_image(PATH: str) -> cv2.Mat:
    
    # Abre a imagem com o OpenCV
    img = cv2.imread(PATH)
    
    # # Exibe a imagem com o pyplot (Para fins de debug)
    # plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # plt.axis('off')
    # plt.show()
    
    return img

# Função para rotacionar a imagem
def rotate_image(image: cv2.Mat, angle: float) -> cv2.Mat:
    
    # Obtém as dimensões da imagem
    (h, w) = image.shape[:2]
    
    # Calcula o centro da imagem
    center = (w/2, h/2)
    
    # Gera a matriz de rotação
    matriz = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # Aplica a rotação à imagem
    rotated = cv2.warpAffine(image, matriz, (w, h), flags=cv2.INTER_CUBIC)
    
    # # Exibe a imagem com o pyplot (Para fins de debug)
    # plt.imshow(cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB))
    # plt.axis('off')
    # plt.show()
    
    return rotated

# Função para extrair o texto da imagem
def extract_text(image: cv2.Mat):
    
    # Aumenta o tamnho da imagem para facilitar a leitura do OCR
    resized = cv2.resize(image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    
    # Coloca a imagem escala de cinza, já que o OCR é mais eficaz com fundo monocromático
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    
    # Criar um leitor OCR e o aplica
    reader= easyocr.Reader(['pt'])
    results = reader.readtext(gray)
    
    text = []
    for detection in results:
        text.append(detection[1].strip())

    return text

# Função para extrair o nome do cliente:
def get_client_name(text: list) -> str:
    
    # Percorre a lista em busca do padrão
    for i, line in enumerate(text):
        
        if 'Referente' in line:
            candidate = text[i-1].strip()
            if re.fullmatch(r'[A-Z]+\s[A-Z]+', candidate):
                return candidate
            
    print('Cliente não encontrado')
    return None

# Função para extrair o número de instalação
def get_instalation_number(text: list) -> str:
    
    # Percorre a lista em busca do padrão
    for i, line in enumerate(text):
        
        if 'INSTALAÇAO' in line:
            candidate = text[i+2].strip()
            if re.fullmatch(r'\d+', candidate):
                return candidate
            
    print('Instalação não encontrado')
    return None

# Função para extrair a cronologia
def get_chronology(text):
    chronology = [None, None, None]  # emissão, vencimento, referente

    for i, line in enumerate(text):

        # Data de emissão
        if chronology[0] is None:
            match = re.search(r'emissão:\s*(\d{2}/\d{2}/\d{4})', line, re.IGNORECASE)
            if match:
                chronology[0] = match.group(1)

        # Data de vencimento
        if chronology[1] is None and 'Vencimento' in line:
            if i + 4 < len(text):
                candidate = text[i + 4].strip()
                match = re.search(r'(\d{2}/\d{2}/\d{4})', candidate)
                if match:
                    chronology[1] = match.group(1)

        # Referente
        if chronology[2] is None and 'Referente' in line:
            if i + 4 < len(text):
                candidate = text[i + 4].strip()
                chronology[2] = re.sub(r'(?<=[A-Za-z])I(?=\d)', '/', candidate)

        if all(chronology):
            return chronology

    print('Algum elemento de cronologia não encontrado')
    return None

# Função para extrair o consumo total
def get_consumption(text):
    
    # Percorre a lista em busca do padrão
    for i, line in enumerate(text):
        
        if 'Consumo kWh' in line:
            candidate = text[i+8]
            if re.fullmatch(r'^\d+$', candidate):
                return int(candidate)
            
    print('Consumo não encontrado')
    return None

# Função para extrair a energia compensada
def get_compensated_energy(text):
    
    # Percorre a lista em busca do padrão
    for i, line in enumerate(text):
        
        if 'compensada' in line:
            candidate = text[i+2]
            if re.fullmatch(r'^\d+$', candidate):
                return int(candidate)
            
    print('Energia Compensada não encontrada')
    return None

# Função para extrair o valor total pago
def get_distributor_value(text):
    
    # Percorre a lista em busca do padrão
    for i, line in enumerate(text):
        
        if 'a pagar' in line.strip():
            candidate = text[i+4]
            match = re.search(r'R\$([0-9]+,[0-9]{2})', candidate)
            if match:
                return float(match.group(1).replace(',', '.'))
            
    print('Valor Distribuidora não encontrado')
    return None

# Função para extrair a tarifa com impostos
def get_tarif(text):
    
    # Percorre a lista em busca do padrão
    for i, line in enumerate(text):
        
        if 'Unit.' in line:
            candidate = text[i+6]
            match = re.search(r'\d+,\d{4,}', candidate)
            if match:
                return float(match.group(0).replace(',', '.'))
            
    print('Tarifa com Impostos não encontrada')
    return None

# Função para extrair a taxa de iluminação pública
def get_street_fee(text):
    
    # Percorre a lista em busca do padrão
    for i, line in enumerate(text):
        
        if 'Ilum' in line:
            candidate = text[i+1]
            match = re.search(r'\d+,\d+', candidate)
            if match:
                return float(match.group(0).replace(',', '.'))
            
    print('Taxa de Iluminação Pública não encontrada')
    return None

# Função para o primeiro cálculo: Valor pago à usina.
def calculate_plant_value(compensated_energy, tarif, discount):
    
    return compensated_energy * tarif * (1 - discount)

# Função para o segundo cálculo: Encargos extras.
def calculate_charges(distributor_value, non_compensated_energy, tarif, street_fee):

    return distributor_value - non_compensated_energy * tarif - street_fee

# Função para formatar valores em reais
def brl(v):
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def main():
    
    # Caminho da imagem da fatura
    IMG_PATH = 'Imagem_fatura_cemig_1.jpg'
    
    # Lê a imagem e guarda em uma matriz 
    raw_img = open_image(IMG_PATH)
    
    # Aplica uma rotação de 5 graus anti-horário
    rotated_img = rotate_image(raw_img, 5)
    
    # Extrai o texto da imagem utilizando OCR
    extracted_text = extract_text(rotated_img)

    # # Exibe o texto extraído
    # for index, line in enumerate(extracted_text):
    #     print(f'Elemento {index}: {line}')
    
    ps_info = {}
    
    # Extrai o nome do cliente
    ps_info['Cliente'] = get_client_name(extracted_text).title()
    
    # Extrai o número de instalação
    ps_info['Número de Instalação'] = get_instalation_number(extracted_text)
    
    # Extrai cronologia
    cronologia = get_chronology(extracted_text)
    
    ps_info['Data de Emissão'] = cronologia[0]
    ps_info['Data de Vencimento'] = cronologia[1]
    ps_info['Mês de Referência'] = cronologia[2]
    
    # Extrai o consumo
    ps_info['Consumo Total (kWh)'] = get_consumption(extracted_text)
    
    # Extrai a Energia Compensada do mês 
    ps_info['Energia Compensada (kWh)'] = get_compensated_energy(extracted_text)
    
    # Extrai Valor Distribuidora (R$)
    ps_info['Valor Distribuidora (R$)'] = get_distributor_value(extracted_text)
    
    # Extrai Tarifa com Impostos
    ps_info['Tarifa com Impostos'] = get_tarif(extracted_text)
    
    # Extrai Taxa de Iluminação Pública
    ps_info['Taxa de Iluminação Pública'] = get_street_fee(extracted_text)
    
    # Imprime os dados extraídos organizados
    for key, value in ps_info.items():
        print(f'{key}: {value}')
    
    # Calcula a primeira fórmula
    v_plant = calculate_plant_value(ps_info['Energia Compensada (kWh)'], ps_info['Tarifa com Impostos'], 0.1)
    
    # Calcula a segunda fórmula
    charges = calculate_charges(ps_info['Valor Distribuidora (R$)'],
        ps_info['Consumo Total (kWh)'] - ps_info['Energia Compensada (kWh)'],\
        ps_info['Tarifa com Impostos'],
        ps_info['Taxa de Iluminação Pública'])
    
    # ================= FORMATADOR =================

    cliente = ps_info['Cliente']
    instalacao = ps_info['Número de Instalação']
    referencia = ps_info['Mês de Referência']
    vencimento = ps_info['Data de Vencimento']

    consumo_total = ps_info['Consumo Total (kWh)']
    energia_comp = ps_info['Energia Compensada (kWh)']
    energia_nao_comp = consumo_total - energia_comp

    tarifa = ps_info['Tarifa com Impostos']
    valor_dist = ps_info['Valor Distribuidora (R$)']
    iluminacao = ps_info['Taxa de Iluminação Pública']

    # Totais simulados
    total_sem_solar = consumo_total * tarifa + charges
    total_com_solar = valor_dist + v_plant
    economia = total_sem_solar - total_com_solar

    print("============================================================")
    print("                FATURA CONSUMIDOR FINAL")
    print("============================================================")
    print(f"Cliente: {cliente:<25} Instalação: {instalacao}")
    print(f"Referência: {referencia:<15} Vencimento: {vencimento}")
    print("------------------------------------------------------------")
    print(f"TOTAL A PAGAR À DISTRIBUIDORA:               R$ {brl(valor_dist)}")
    print("------------------------------------------------------------\n")

    print("VALOR A PAGAR À USINA")
    print("------------------------------------------------------------")
    print(f"{'Descrição':<22}{'Qtd':>6}{'Tarifa':>10}{'Valor':>12}")
    print(f"{'Energia Compensada':<22}{energia_comp:>6}"
        f"{tarifa:>10.3f}{brl(v_plant):>12}\n")

    print("FATURA SEM ENERGIA SOLAR")
    print("------------------------------------------------------------")
    print(f"{'Descrição':<22}{'Qtd':>6}{'Tarifa':>10}{'Valor':>12}")
    print(f"{'Consumo Energia Total':<22}{consumo_total:>6}"
        f"{tarifa:>10.2f}{brl(consumo_total*tarifa):>12}")
    print(f"{'Outros Encargos':<22}{'-':>6}{'-':>10}{brl(charges):>12}")
    print(f"{'Taxa Iluminação':<22}{'-':>6}{'-':>10}{brl(iluminacao):>12}")
    print("------------------------------------------------------------")
    print(f"{'TOTAL SEM SOLAR':<38}R$ {brl(total_sem_solar)}\n")

    print("FATURA COM ENERGIA SOLAR")
    print("------------------------------------------------------------")
    print(f"{'Descrição':<22}{'Qtd':>6}{'Tarifa':>10}{'Valor':>12}")
    print(f"{'Energia Não Compensada':<22}{energia_nao_comp:>6}"
        f"{tarifa:>10.2f}{brl(energia_nao_comp*tarifa):>12}")
    print(f"{'Energia Compensada':<22}{energia_comp:>6}"
        f"{tarifa:>10.3f}{brl(v_plant):>12}")
    print(f"{'Outros Encargos':<22}{'-':>6}{'-':>10}{brl(charges):>12}")
    print(f"{'Taxa Iluminação':<22}{'-':>6}{'-':>10}{brl(iluminacao):>12}")
    print("------------------------------------------------------------")
    print(f"{'TOTAL COM SOLAR':<38}R$ {brl(total_com_solar)}\n\n")

    print("RESUMO DE ECONOMIA")
    print("------------------------------------------------------------")
    print(f"{'TOTAL SEM SOLAR':<38}R$ {brl(total_sem_solar)}")
    print("------------------------------------------------------------")
    print(f"{'TOTAL COM SOLAR':<38}R$ {brl(total_com_solar)}")
    print("------------------------------------------------------------")
    print(f"{'ECONOMIA CALCULADA':<38}R$ {brl(economia)}")
    print("------------------------------------------------------------\n")

    print(f"{'TOTAL A PAGAR':<38}R$ {brl(v_plant)}")
    print("============================================================")
    
if __name__ == "__main__":   
    main()
    
    
    