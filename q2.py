import pandas as pd
import zipfile
import os
import requests
from bs4 import BeautifulSoup
import math
from validate_docbr import CNPJ


def validacao(nome_arquivo):
    consolidado = pd.read_csv(nome_arquivo)

    validador = CNPJ()

    # validar cnpj

    consolidado['CNPJ'] = consolidado['CNPJ'].drop_duplicates().reset_index(drop=True) # remove duplicatas

    consolidado['CNPJ'] = consolidado['CNPJ'].astype(str).str.replace(r'\D', '', regex=True)# extirpa elementos diferentes de dígitos

    consolidado['CNPJ'] = consolidado['CNPJ'].str.zfill(14) # garante que 

    consolidado = consolidado[consolidado['CNPJ'].str.len() == 14]

    consolidado = consolidado[consolidado['CNPJ'] != '00000000000000'] # extirpa cnpjs zerados.

    consolidado = consolidado[consolidado['CNPJ'].apply(lambda x: validador.validate(x))] # valida os dígitos do CNPJ com a biblioteca validate_docbr

    # validar gastos

    consolidado = consolidado[consolidado['ValorDespesas'] > 0]  # falsos ou desimportantes para a contablização.

    consolidado = consolidado[consolidado['RazaoSocial'].str.len() != 0] # Razão social não pode estar vazia.

    












