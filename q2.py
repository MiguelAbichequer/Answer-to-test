import pandas as pd
import zipfile
import requests
import numpy as np
from validate_docbr import CNPJ


def validacao(nome_arquivo):
    consolidado = pd.read_csv(nome_arquivo, sep=';', encoding='latin-1')
    validador = CNPJ()

    def limpar_cnpj(val):
        try:
            return str(int(float(val))).zfill(14)
        except:
            return str(val).replace('.', '').replace('-', '').replace('/', '').zfill(14)

    consolidado['CNPJ'] = consolidado['CNPJ'].apply(limpar_cnpj)

    consolidado = consolidado[consolidado['CNPJ'].str.len() == 14]
    consolidado = consolidado[consolidado['CNPJ'] != '00000000000000']
    
    # validação final com biblioteca
    mask_valid = consolidado['CNPJ'].apply(lambda x: validador.validate(x))
    consolidado = consolidado[mask_valid]

    # Validar gastos
    consolidado['ValorDespesas'] = pd.to_numeric(consolidado['ValorDespesas'], errors='coerce')
    consolidado = consolidado[consolidado['ValorDespesas'] > 0]
    consolidado = consolidado.dropna(subset=['RazaoSocial'])

    return consolidado.drop_duplicates().reset_index(drop=True)

def baixar_arquivo(url, endereco):

    requisicao = requests.get(url)

    with open(endereco, 'wb') as novo_arquivo:
        novo_arquivo.write(requisicao.content)

def consolidar_dados(dataFrame):

    baixar_arquivo("https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv", "Relatorio_cadop.csv")

    # dataFrame = preparar_arquivo(dataFrame)

    df_cadastro = pd.read_csv('Relatorio_cadop.csv', sep=';', encoding='latin-1', dtype={'CNPJ': str})

    joined_df = pd.merge(
        dataFrame,
        df_cadastro, 
        on='CNPJ',
        how='left'      
    )

    colunas_finais = ['CNPJ', 'RazaoSocial', 'ValorDespesas', 'ANO', 'TRIMESTRE', 'Data_Registro_ANS', 'Modalidade', 'UF']
    joined_df = joined_df[colunas_finais]

    return joined_df

def preparar_arquivo(dataFrame):

    dataFrame['Data_Registro_ANS'] = np.nan
    dataFrame['Modalidade'] = np.nan
    dataFrame['UF'] = np.nan

    return dataFrame

def calcular(dataFrame):
    dataFrame_agrupado = dataFrame.groupby(['UF', 'RazaoSocial'])['ValorDespesas'].agg(['sum', 'mean', 'std'])
    # agrupa por UF e RazaoSocial e calcula a média e o somatório das despesas

    dataFrame_agrupado.columns = ['Total_Despesas', 'Media_Despesas', 'Desvio_Padrao']
    dataFrame_agrupado = dataFrame_agrupado.fillna(0)
    # preencher valores NaN com 0
    # pois UF e Razão Social são colunas índice

    dataFrame_agrupado = dataFrame_agrupado.sort_values(by='Total_Despesas', ascending=False)

    dataFrame_agrupado = dataFrame_agrupado.round(4)

    return dataFrame_agrupado.reset_index()

if __name__ == "__main__":

    df_validado = validacao("consolidado_despesas.csv")

    df_consolidado = consolidar_dados(df_validado)

    df_consolidado = calcular(df_consolidado)

    print(df_consolidado)

    df_consolidado.to_csv("despesas_agregadas.csv", index=False, sep=';', float_format='%.2f')

    with zipfile.ZipFile('Teste_Miguel_Abichequer.zip', 'w') as zipf:
        zipf.write('despesas_agregadas.csv')

