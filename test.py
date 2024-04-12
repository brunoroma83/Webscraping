import pandas as pd
from bs4 import BeautifulSoup
import pandas as pd

df = pd.read_json('dicionario2.json')
html_tudo = df.to_dict('records')
dic_info = {
    'Alerta': [],
    'Descrição da Classe': [],
    'Produto': [],
    'Problema': [],
    'Ação': [],
    'Esclarecimento': [],
    'Fonte': [],
    'Data da ocorrência': [],
    'Fabricante': [],
    'Lista de distribuição': []
}

for alerta in html_tudo:
    soup = BeautifulSoup(alerta['HTML'], 'html.parser')
    i = 0
    p = soup.find('label', 'Descrição da Classe')
    
    for i in range(1, len(p)+1):
        print(f'{i}: {p.find_all_next()}')
        i = i+1
        if i == 3: break

