import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_page():
    
    dicionario = {'Alerta': [], 'HTML': []}
    nome_arquivo_json = 'dicionario2.json'
    ultimo_alerta_carregado = 0
    try:
        with open(nome_arquivo_json, 'r') as f:
            df1 = pd.read_json(nome_arquivo_json)
            #fazer código para pegar o último alerta
            df1['Alerta']=pd.to_numeric(df1['Alerta'])
            ultimo_alerta_carregado = int(df1['Alerta'].max())
            dicionario_carregado = True
    except IOError:
        dicionario_carregado = False    
    url = 'http://antigo.anvisa.gov.br/alertas?pagina=1'
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    #n_alerta = soup.find_all('div', class_='row-fluid lista-noticias')
    titulo = soup.find('p', class_='titulo').text.strip()
    print(f'titulo={titulo}')
    alerta_mais_recente = int(titulo[7:12].strip())

    # acessar a paginação do site
    print(f'range({ultimo_alerta_carregado}+1, {alerta_mais_recente})')
    for i in range(ultimo_alerta_carregado+1, alerta_mais_recente):
        dicionario['Alerta'].append(i)
        url = f'https://www.anvisa.gov.br/sistec/Alerta/RelatorioAlerta.asp?NomeColuna=CO_SEQ_ALERTA&Parametro={i}'
        print(url)
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')
        print(soup.find_all('table')[1])
        dicionario['HTML'].append(str(soup.find_all('table')[1]))    
   
    print('fim do scrape')
    df = pd.DataFrame(dicionario)
    df_fim = pd.concat([df1, df], ignore_index=True)
    df_fim.to_json('dicionario2.json', force_ascii=False, )       
            
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
}

scrape_page()