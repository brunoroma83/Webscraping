# os alertas antigos confundem o script e não consegue identificar a empresa
# então vou fazer uma lista de empresas e relacionar com os números de registro anvisa

import pandas as pd
import gemini_api
import json

dic_alertas = 'dicionario.json'
empresas = {'Raiz do Registro': [], 'Empresa':[]}

try:
    with open(dic_alertas, 'r', encoding='utf-8') as arquivo:
        df = pd.read_json(arquivo)
        alertas = df.to_dict('records')
except (FileNotFoundError, json.JSONDecodeError):
    print(f'Erro. Não existe arquivo {dic_alertas}')

i=0

for x in alertas:
    n_registro = x['Número de registro ANVISA'].split(';')[0][:7]
    if "não encontrado" in x['Empresa']: continue
    else:
        if not n_registro in empresas['Raiz do Registro'] and n_registro.isdigit(): 
            empresas['Raiz do Registro'].append(n_registro)
            # arrumar os nomes de empresas que tem qualquer coisa depois de LTDA
            n = x['Empresa'].lower()
            if 'ltda' in n: nome_empresa = x['Empresa'][:n.find('ltda')+4]
            else: nome_empresa = x['Empresa']
            empresas['Empresa'].append(nome_empresa)
    i = i+1
    df_novo = pd.DataFrame(empresas)
    df_novo.to_json('empresas.json', force_ascii=False)
    #if i==10: break
    