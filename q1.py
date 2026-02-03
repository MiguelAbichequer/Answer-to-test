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

    baixar_arquivo("https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv", "Relatorio_cadop.csv")
    
    requisicao = requests.get(url)
    # obter informações contidas na pasta do ano selecionado

    dados_pagina = BeautifulSoup(requisicao.text, 'html.parser')

    arquivos = dados_pagina.find_all("a", href=lambda h: h and h.endswith(".zip"))

    lista_nomes = []

    count = 0  # para pegar apenas os últimos 3 trimestres
    for arq in arquivos:
        lista_nomes.append(arq['href'])  # salva os nomes dos arquivos que serão baixados e descompactados.
        count = count + 1
        if count == 3:
            break
    
    uniao_df = []
    # 1 - baixar arquivos, descompactar e filtrar.

    for nome in lista_nomes:
        link = url + nome
        endereco = nome
        baixar_arquivo(link, endereco)
        df = descompacta_e_filtra(nome)
        uniao_df.append(df)
    
    resultado = pd.concat(uniao_df)  # une todos os campos de interesse contidos na faixa de tempo analisada.

    print("carregando arquivo de cadastro...")

    df_cadastro = pd.read_csv('Relatorio_cadop.csv', sep=';', dtype={'CNPJ': str}) # ler o arquivo de cadastro

    df_consolidado = pd.merge(resultado[['REG_ANS', 'DATA', 'VL_SALDO_FINAL']], df_cadastro[['REGISTRO_OPERADORA', 'CNPJ', 'Razao_Social']], left_on='REG_ANS', right_on='REGISTRO_OPERADORA', how='left')

    
    df_consolidado['DATA'] = pd.to_datetime(df_consolidado['DATA']) # transforma o tipo coluna DATA em datetime64 
    df_consolidado['ANO'] = df_consolidado['DATA'].dt.year  # separa o ano
    df_consolidado['TRIMESTRE'] = df_consolidado['DATA'].dt.quarter.astype(str) + 'T' # separa o trimestre

    # valores

    df_consolidado['ValorDespesas'] = pd.to_numeric(df_consolidado['VL_SALDO_FINAL'].str.replace('.', '').str.replace(',', '.'), errors='coerce')

    # transforma o tipo da coluna VL_SALDO_FINAL em float, substituindo o separador decimal brasileiro (',') pelo internacional ('.')

    # remover valores zero ou negativos

    df_consolidado = df_consolidado[df_consolidado['ValorDespesas'] > 0]  # falsos ou desimportantes para o somatório.

    # padronizar CNPJ

    df_consolidado['RazaoSocial'] = df_consolidado.groupby('CNPJ')['Razao_Social'].transform('last')

    # CONSOLIDAR

    colunas_finais = ['CNPJ', 'RazaoSocial', 'ANO', 'TRIMESTRE', 'ValorDespesas']

    df_consolidado = df_consolidado[colunas_finais].drop_duplicates().reset_index(drop=True) # remove duplicatas e reseta o índice das colunas

    return df_consolidado

def selecionar_ano(url):

    requisicao = requests.get(url)
    dados_pagina = BeautifulSoup(requisicao.text, 'html.parser')

    anos = dados_pagina.find_all("a")  
    # para separar os links correspondetes a cada um dos anos.

    lista = []
    

    for ano in anos:
        if(ano['href'].startswith(("20", "19"))):  # para evitar valores lixo, separamos somente os anos.
            lista.append(int(ano['href'][:4]))  # cortar a string para seperar somente o ano.
    
    ano_mais_recente = max(lista)  # o ano mais recente é também o maior de todos eles.

    ano_mais_recente = str(ano_mais_recente) + '/'  # para concataner e formar o link

    link = url + ano_mais_recente

    return link


        

def buscar(df):
    if 'DESCRICAO' not in df.columns:
        print("Coluna 'DESCRICAO' não encontrada no arquivo.")
        return pd.DataFrame()  # DataFrame vazio se a coluna não existir
    # DES = df[df['DESCRICAO'] == "Despesas com Eventos/Sinistros - Judicial"]  # filtro coluna DESCRICAO
    DES = df[df['CD_CONTA_CONTABIL'].astype(str).str.startswith('411')]
    return DES


def descompacta_e_filtra(nome_arquivo):
    zip_path = nome_arquivo
    zip_dir = "extractedFiles"

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(zip_dir) # abre o arquivo zip
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


if __name__ == "__main__":
    url = "https://dadosabertos.ans.gov.br/FTP/PDA/"

    url_doc = achar_link(url)

    url_ano = selecionar_ano(url_doc)

    novo = preparar_arquivos(url_ano)

    print(novo)

    novo.to_csv('consolidado_despesas.csv', sep=';')

