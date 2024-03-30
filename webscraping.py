# monitoramento de alertas de tecnoviligância no site da Anvisa
# O programa para entrar no site da Anvisa Alertas de Tecnovigilância (OK)
# fazer um web scraping dos alertas (OK)
# salvar as informações em banco de dados (a princício Google Sheets) (parcial)
# o programa deve rodar diariamente as 00:00 automaticamente

# Objetivo principal: fazer um relatório diário e um mensal automaticamente, informando um resumo dos novos alertas
# o programa deve ainda comparar se algum novo alerta contém o mesmo registro Anvisa de algum equipamento da base
# havendo equipamento na base com alerta novo, deve incluir no relatório
# Objetivo secundário: permitir pesquisa dos alertas por fabricante, registro anvisa, nome comercial, nome técnico, por data
# permitir pesquisa por API para integrações

# como não consegui conectar no Google Sheets com om Python vou fazer o scrape com o python
# verificar se há novos alertas e salvar os alertas no arquivo dicionario.JSON
# o Google App Script vai pegar o dicionario e alimentar a planilha
# Como verificar se houve novo alerta alimentado?
# no Google App Script podemos verificar se o número do alerta da última alimentação é igual
# ao 
# 25/01/2024 vou tentar comparar a lista de notificações com uma lista de números de registro ANVISA da minha base
# com o objetivo de criar um relatório toda vez que o programa for rodado
# a versão gratuita do PythonAnyWhere.com não suporta acessar urls fora da whitelist (https://www.pythonanywhere.com/whitelist/)
# ou seja, não é possível scanear o site da Anvisa com a versão gratuita

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pandas as pd

def logger(dados, nome_arquivo='log.json'):
    # Carregar dados existentes, se houver
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
            logs_existente = json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        logs_existente = []

    # Adicionar novos dados
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    novo_log = {'data-hora término': data_hora, 'dados': dados}
    logs_existente.append(novo_log)

    # Salvar os dados atualizados no arquivo JSON
    with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
        json.dump(logs_existente, arquivo, ensure_ascii=False)

def scrape_page(datahoje,max_paginas=200):
    # acessar até a página 230 depois disso dá erro
    # carregar dicionario json
    nome_arquivo_json = 'dicionario.json'
    dicionario = {'Alerta': [],
                   'Data do alerta': [],
                   'URL': [],
                   'Resumo': [],
                   'Identificação do produto ou caso': [],
                   'Problema': [],
                   'Ação': [],
                   'Referências': [],
                   'Histórico': [],
                   'Recomendações': [],
                   'Anexos': [],
                   'Informações Complementares': [],
                   'Empresa': [],
                   'Nome Comercial': [],
                   'Nome Técnico': [],
                   'Número de registro ANVISA': [],
                   'Tipo de produto': [],
                   'Classe de Risco': [],
                   'Modelo afetado': [],
                   'Números de série afetados': []}

    #verificar se o dicionário existe, se sim carrega, se não segue
    ultimo_alerta_carregado = 0
    try:
        with open(nome_arquivo_json, 'r') as f:
            df = pd.read_json(nome_arquivo_json)
            #fazer código para pegar o último alerta
            df['Alerta']=pd.to_numeric(df['Alerta'])
            ultimo_alerta_carregado = str(df['Alerta'].max())
            dicionario_carregado = True
    except IOError:
        dicionario_carregado = False        

    finalizar = False 

    # acessar a paginação do site
    for i in range(1, max_paginas+1):
        if (finalizar): break
        url = f'http://antigo.anvisa.gov.br/alertas?pagina={i}'
        print(url)
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')
        noticias_alerta = soup.find_all('div', class_='row-fluid lista-noticias')
        
        for quote_element in noticias_alerta:

            list_temp = {}
            list_temp.clear()        

            titulo = quote_element.find('p', class_='titulo').text.strip()
            num_alerta = titulo[7:12].strip()
            list_temp['Alerta'] = num_alerta

            if ultimo_alerta_carregado == num_alerta:
                logger('último alerta carregado igual ao alerta encontrado')
                print('último alerta carregado igual ao alerta encontrado')
                finalizar = True
                break
        
            data = quote_element.find('div', class_='span3 data-hora').text.strip()[:10]
            list_temp["Data do alerta"] = data
            titulo_link = quote_element.find('a', href=True)['href']
            list_temp["URL"] = titulo_link

            subpage = requests.get(titulo_link, headers=headers)
            subsoup = BeautifulSoup(subpage.text, 'html.parser')
            subpage_elements = subsoup.find('div', class_='bodyModel')
            print(num_alerta)
            #if not str(subpage_elements).find('h4') > 0:
            if not num_alerta.isdigit() or not str(subpage_elements).find('h4') > 0:
                print(f'não encontrou números no alerta: {num_alerta}')
                logger(f'não encontrou números no alerta: {num_alerta}')
                continue

            for elemento in subpage_elements(['h4','p','a']): #os elementos podem ter H4 e P
                
                if str(elemento).find('h4') > 0: #se tem h4 é uma chave do dicionário
                    chave_dic = remover_nao_alfabeticos(elemento.text)
                else:
                    #primeiro verifica se tem link para entrar no modo de salvar os links
                    a = elemento.find_all('a', href=True)
                    if a:
                        for a in elemento.find_all('a', href=True):
                            if chave_dic in list_temp:
                                list_temp[chave_dic] += f" {a.text} => (https://antigo.anvisa.gov.br{a['href']})."
                            else: 
                                list_temp[chave_dic] = f"{a.text} => (https://antigo.anvisa.gov.br{a['href']})."
                    else: #caso não tenha link, segue com a inclusão normal
                        if chave_dic in list_temp:
                            list_temp[chave_dic] = f"{list_temp[chave_dic]} {str(elemento.text).strip()}"
                        else:
                            list_temp[chave_dic] = str(elemento.text).strip()
               
            if "Resumo" in list_temp:
                r = list_temp['Resumo']
                #list_temp['Nome Comercial:'] = r[r.rfind('- ')+2:-1].strip()
                if r.find('empresa ') > 0:
                    list_temp['Empresa'] = r[r.find('empresa ')+8:r.rfind(' -')].strip()
            if "Ação:" in list_temp:
                r = list_temp['Ação']
                #list_temp['Nome Comercial:'] = r[r.rfind('- ')+2:-1].strip()
                if r.lower().find('empresa ') > 0 and not 'Empresa' in list_temp:
                    list_temp['Empresa'] = r[r.find('empresa ')+8:r.find('.')].strip()
            if not "Empresa" in list_temp:
                list_temp["Empresa"] = "não encontrado"
            # for para iniciar as chaves com algum conteúdo
            list_chave = ['Nome Comercial','Nome Técnico','Número de registro ANVISA','Tipo de produto','Classe de Risco','Modelo afetado','Números de série afetados']
            for chave in list_chave:
                list_temp[chave] = "não encontrado"
            if "Identificação do produto ou caso" in list_temp:
                r = list_temp["Identificação do produto ou caso"]
                r_lc = r.lower()    
                for i in range(0, len(list_chave)):
                    if r_lc.find(list_chave[i].lower()) >= 0:
                        if i == len(list_chave) - 1:
                            list_temp[list_chave[i]] = r[r_lc.find(list_chave[i].lower())+len(list_chave[i])+2:].strip()                          
                        else:
                            list_temp[list_chave[i]] = r[r_lc.find(list_chave[i].lower())+len(list_chave[i])+2:r_lc.find(list_chave[i+1].lower())].strip()

                        try:
                            if '.' == list_temp[list_chave[i]][-1] and len(list_chave[i]) > 0:
                                list_temp[list_chave[i]] = list_temp[list_chave[i]][:-1]
                        except:
                            continue
            else:
                list_temp['Identificação do produto ou caso'] = "não encontrado"
            
            logger(f'Alerta adicionado: {num_alerta}')
            #incluir dados do alerta no dicionario
            for chave, valor in dicionario.items():
                if chave in list_temp: dicionario[chave].append(list_temp[chave])
                else: dicionario[chave].append(' ')
   
    logger("fim do scrape")
    print('fim do scrape')
    df_novo = pd.DataFrame(dicionario)
    # antes de salvar o dicionario, precisar juntar os dois dicionarios
    if dicionario_carregado: 
        df = pd.concat([df, df_novo], ignore_index=True)
    else: 
        df = df_novo    
    df.to_json(f'dicionario.json', force_ascii=False)
            
def remover_nao_alfabeticos(texto):
    for caractere in ":;.!@#$%^&*()-+?_=,<>/0123456789":
        texto = texto.replace(caractere, "")
    return texto

def gravarDicionario(dicio, nome_dic='dicionario.json'):
    with open(nome_dic, "w", encoding="utf-8") as file:
        json.dump(dicio, file, ensure_ascii=False)
    logger("Dicionário gravado")

    # Carregar dados existentes, se houver
    try:
        with open(nome_dic, 'r', encoding='utf-8') as arquivo:
            dicio_existente = json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        dicio_existente = []
        dicio_existente.append(dicio.copy())

    # Salvar os dados atualizados no arquivo JSON
    with open(nome_dic, 'w', encoding='utf-8') as arquivo:
        json.dump(dicio_existente, arquivo, ensure_ascii=False)

 
        
            
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
}

def converter_xlx_json(arquivo):
# Load Excel to DataFrame
    path_excel = arquivo
    df = pd.read_excel(path_excel, engine='openpyxl')

    # Convert DataFrame to JSON
    equipamentos_json = df.to_json(orient='records', indent=4, force_ascii=False)

    # Write JSON data to file
    #arquivo_json = f'{arquivo[:-4]}json'
    path_json = f'{arquivo[:-4]}json'
    with open(path_json, 'w', encoding='utf-8') as json_file:
        json_file.write(equipamentos_json)

# objetivo é analilsar o banco de dados e criar um arquivo json contendo as correspondências reg anvisa e alertas
def separar_alertas():

    nome='dicionario.json'
    df = pd.read_json(nome)
    dicionario = df.to_dict('records')    
    reg_anvisa_alerta = {'Alerta':[],'Número de registro ANVISA':[]}

    i = 0
    for x in dicionario:
        alerta = x['Alerta']
        reg_anvisa = str(x['Número de registro ANVISA']).split(';')
        for x in reg_anvisa:
            reg_anvisa_alerta['Alerta'].append(str(alerta))
            reg_anvisa_alerta['Número de registro ANVISA'].append(x.strip())
            #reg_anvisa_alerta = pd.concat([reg_anvisa_alerta, temp_df], ignore_index=True)
            #print(f'{alerta} -> reg anvisa: "{x}"')
        #i += 1
        if i > 5: break
    df_reg = pd.DataFrame(reg_anvisa_alerta)
    #print(df_reg.info)
    df_reg.to_json('reg_anvisa_alerta.json', force_ascii=False)
    return df_reg

def buscar_registro_anvisa(registro_anvisa):
    df_reg = separar_alertas()
    #print(df_reg.value_counts('Número de registro ANVISA'))
    df_reg_filtrado = df_reg.loc[df_reg['Número de registro ANVISA'].isin(registro_anvisa)]
    #return df_reg_filtrado
    if df_reg_filtrado.empty: return pd.DataFrame({'erro': f'Nenhum alerta encontrado para {registro_anvisa}'}, index=[0])
    else: return(df_reg_filtrado)

logs = []

d = {'data-hora início': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

logger(d)

scrape_page(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),300)

imprimir = separar_alertas()
print(imprimir.info())

