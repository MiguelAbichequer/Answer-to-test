import pandas as pd
import zipfile
import os
import requests
from bs4 import BeautifulSoup

def achar_link(url):
    requisicao = requests.get(url)
    dados_pagina = BeautifulSoup(requisicao.text, 'html.parser')
    link = dados_pagina.find_all("a", href=lambda h: h and "demonstracoes_contabeis" in h)
    # encontra todas as ocorrências de links que contenham "demonstracoes_contabeis"
    
    link = url + link[0]['href']
    return link

def baixar_arquivo(url, endereco):

    requisicao = requests.get(url)
    # acessa o link encontrado para a pasta correspondente

    with open(endereco, 'wb') as novo_arquivo:
        novo_arquivo.write(requisicao.content)

def preparar_arquivos(url):

    requisicao = requests.get(url)
    # obter informações contidas na pasta do ano selecionado

    dados_pagina = BeautifulSoup(requisicao.text, 'html.parser')

    arquivos = dados_pagina.find_all("a", href=lambda h: h and h.endswith(".zip"))

    lista_nomes = []

    count = 0 # para pegar apenas os últimos 3 trimestres
    for arq in arquivos:
        lista_nomes.append(arq['href']) # salva os nomes dos arquivos que serão baixados e descompactados.
        count = count + 1
        if count == 2:
            break


    # 1 - baixar arquivos

    for nome in lista_nomes:
        link = url + nome
        endereco = nome
        baixar_arquivo(link, endereco)

    
        




def selecionar_ano(url):

    requisicao = requests.get(url)
    dados_pagina = BeautifulSoup(requisicao.text, 'html.parser')

    anos = dados_pagina.find_all("a") # para separar os links correspondetes a cada um dos anos.

    lista = []
    

    for ano in anos:
        if(ano['href'].startswith(("20", "19"))): # para evitar valores lixo, separamos somente os anos.
            lista.append(int(ano['href'][:4])) # cortar a string para seperar somente o ano.
    
    ano_mais_recente = max(lista) # o ano mais recente é também o maior de todos eles.

    ano_mais_recente = str(ano_mais_recente) + '/' # para concataner e formar o link

    link = url + ano_mais_recente

    return link


        

def buscar(df):
    if 'DESCRICAO' not in df.columns:
        print("Coluna 'DESCRICAO' não encontrada no arquivo.")
        return pd.DataFrame()  # DataFrame vazio se a coluna não existir
    DES = df[df['DESCRICAO'] == "Despesas com Eventos/Sinistros - Judicial"]  # filtro coluna DESCRICAO
    return DES


def descompacta_e_filtra(nome_arquivo):
    zip_path = nome_arquivo
    zip_dir = "extractedFiles"

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(zip_dir)
        for nome_interno in zip_ref.namelist():

            print(nome_interno)
            new_csv = pd.DataFrame()
            ultimos_tres = nome_interno[-3:]
            ultimos_tres = ultimos_tres.lower()

            if ultimos_tres == 'csv' or ultimos_tres == 'txt':
                df = pd.read_csv(os.path.join(zip_dir, nome_interno), sep=';')
                new_csv = buscar(df)
            elif ultimos_tres == 'lsx':
                df = pd.read_excel(os.path.join(zip_dir, nome_interno))
                new_csv = buscar(df)
            else:
                print("Formato de arquivo inválido")

        if not new_csv.empty:
            return new_csv
        


###

###


if __name__ == "__main__":
    url = "https://dadosabertos.ans.gov.br/FTP/PDA/"

    url_doc = achar_link(url)

    url_ano = selecionar_ano(url_doc)

    preparar_arquivos(url_ano)

    





