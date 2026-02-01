import pandas as pd
import zipfile
import os


def buscar(df):
    if 'DESCRICAO' not in df.columns:
        print("Coluna 'DESCRICAO' não encontrada no arquivo.")
        return pd.DataFrame()  # DataFrame vazio se a coluna não existir
    DES = df[df['DESCRICAO'] == "Despesas com Eventos/Sinistros - Judicial"]  # filtro coluna DESCRICAO
    return DES

def dados(nome_arquivo):
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

        return new_csv

resultado = dados("1T2025.zip")

print(resultado)









