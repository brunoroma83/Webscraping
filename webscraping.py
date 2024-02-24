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


def carregar_json(nome_arquivo):
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
            dados_json = json.load(arquivo)
        return dados_json
    except FileNotFoundError:
        logger(f"O arquivo '{nome_arquivo}' não foi encontrado.")
        return {}
    except json.JSONDecodeError:
        logger(f"Erro ao decodificar o JSON no arquivo '{nome_arquivo}'. Verifique a formatação do JSON.")
        return {}

def scrape_page(datahoje,max_paginas=200):
    # acessar até a página 230 depois disso dá erro
    # carregar dicionario json
    nome_arquivo_json = 'dicionario.json'
    dicionario_carregado = dict()
    dicionario = dict()
    dicionario_carregado = carregar_json(nome_arquivo_json)
    
    #Verificar a última linha do dicionnario carregado
    ultimo_alerta_carregado = "0"
    if type(dicionario_carregado) is dict:
        for alerta_carregado in dicionario_carregado:
            #print(f'{alerta_carregado=}')
            if ultimo_alerta_carregado < alerta_carregado:
                ultimo_alerta_carregado = alerta_carregado
            #print(f'{ultimo_alerta_carregado=}')
        #dicionario = dicionario_carregado.copy()
    
    # acessar a paginação do site
    for i in range(1, max_paginas+1):
        url = f'http://antigo.anvisa.gov.br/alertas?pagina={i}'
        print(url)
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')
        noticias_alerta = soup.find_all('div', class_='row-fluid lista-noticias')
        
        for quote_element in noticias_alerta:

            list_temp = {}
            list_temp.clear()        

            # pegar o número do alerta e verificar se já está na base

            titulo = quote_element.find('p', class_='titulo').text.strip()
            num_alerta = titulo[7:12].strip()
            list_temp['Número do alerta:'] = num_alerta

            if ultimo_alerta_carregado == num_alerta:
                logger('último alerta carregado igual ao alerta encontrado')
                
                #chamar relatório do scrape antes de sair
                relatorio_geral(dicionario,f"relatorios/relatorio_scrape_{datahoje}.json",dicionario)
                if type(dicionario_carregado) is dict:
                    dicionario.update(dicionario_carregado)
                gravarDicionario(dicionario)
                return
        
            data = quote_element.find('div', class_='span3 data-hora').text.strip()[:10]
            list_temp["Data do alerta:"] = data
            titulo_link = quote_element.find('a', href=True)['href']
            list_temp["Link do alerta:"] = titulo_link

            subpage = requests.get(titulo_link, headers=headers)
            subsoup = BeautifulSoup(subpage.text, 'html.parser')
            subpage_elements = subsoup.find('div', class_='bodyModel')
            print(num_alerta)
            #if not str(subpage_elements).find('h4') > 0:
            if not num_alerta.isdigit() or not str(subpage_elements).find('h4') > 0:
                print(f'não encontrou números no alerta: {num_alerta}')
                logger(f'não encontrou números no alerta: {num_alerta}')
                continue

            for elemento in subpage_elements(['h4','p']): #os elementos podem ter H4 e P
                
                if str(elemento).find('h4') > 0: #se tem h4 é uma chave do dicionário
                    chave_dic = elemento.text
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
               
            if "Resumo:" in list_temp:
                r = list_temp['Resumo:']
                #list_temp['Nome Comercial:'] = r[r.rfind('- ')+2:-1].strip()
                if r.find('empresa ') > 0:
                    list_temp['Empresa:'] = r[r.find('empresa ')+8:r.rfind(' -')].strip()
            if "Ação:" in list_temp:
                r = list_temp['Ação:']
                #list_temp['Nome Comercial:'] = r[r.rfind('- ')+2:-1].strip()
                if r.lower().find('empresa ') > 0 and not 'Empresa:' in list_temp:
                    list_temp['Empresa:'] = r[r.find('empresa ')+8:r.find('.')].strip()
            if not "Empresa:" in list_temp:
                list_temp["Empresa:"] = "não encontrado"
            # for para iniciar as chaves com algum conteúdo
            list_chave = ['Nome Comercial:','Nome Técnico:','Número de registro ANVISA:','Tipo de produto:','Classe de Risco:','Modelo afetado:','Números de série afetados:']
            for chave in list_chave:
                list_temp[chave] = "não encontrado"
            if "Identificação do produto ou caso:" in list_temp:
                r = list_temp["Identificação do produto ou caso:"]
                r_lc = r.lower()    
                for i in range(0, len(list_chave)):
                    if r_lc.find(list_chave[i].lower()) >= 0:
                        if i == len(list_chave) - 1:
                            list_temp[list_chave[i]] = r[r_lc.find(list_chave[i].lower())+len(list_chave[i]):].strip()                          
                        else:
                            list_temp[list_chave[i]] = r[r_lc.find(list_chave[i].lower())+len(list_chave[i]):r_lc.find(list_chave[i+1].lower())].strip()

                        try:
                            if '.' == list_temp[list_chave[i]][-1] and len(list_chave[i]) > 0:
                                list_temp[list_chave[i]] = list_temp[list_chave[i]][:-1]
                        except:
                            continue
            else:
                list_temp['Identificação do produto ou caso:'] = "não encontrado"
            
            logger(f'Alerta adicionado: {num_alerta}')
            dicionario[num_alerta]= {}
            dicionario[num_alerta]=list_temp.copy()

        
    #antes do final do scrape, fazer o relatório do scrape com os equipamentos
    dicio_fim = {}
    dicio_fim["Alertas encontrados"] = dicionario.copy()
    dicio_fim['Alertas encontrados']['Quantidade'] = len(dicionario)
    relatorio_geral(dicionario,f"relatorios/relatorio_scrape_{datahoje}.json",dicio_fim)
    if type(dicionario_carregado) is dict:
        dicionario.update(dicionario_carregado)
    
    gravarDicionario(dicionario)
       
    logger("fim do scrape")
            


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

    #df = pd.DataFrame(data=dicio_existente, index=[1])
    #df = (df.T)
    #df.to_excel(f'{nome_dic[:-5]}.xlsx', index=False)
    #Salvar em Excel
    #with pd.ExcelWriter(f'{nome_dic[:-5]}.xlsx', engine='openpyxl') as writer:
    # 2. Export data
    #    dicio_existente.to_excel(writer, sheet_name='Relatório')
        
            
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



def relatorio_geral(alertas_json=carregar_json('dicionario.json'),nome_relatorio='relatorios/relatorio_geral.json',dicio_adicionar={}):
    #converter o arquivo xlsx em json
    #converter_xlx_json('equipamentos.xlsx')

    #carregar os equipamentos
    equipamentos = carregar_json('equipamentos.json')

    #criar uma nova tabela reg_anvisa relacionando números de registro anvisa e quais equipamentos estão relacionados a estes números de registo
    #será necessário criar uma lista para cada key do dicionário
    reg_anvisa = dict()
    for equipamento in equipamentos:
        if equipamento["Situação"] == "Desativado":
            continue
        registro = str(equipamento["Número Registro Anvisa"])[:-2]
        if len(registro) >= 8:
            reg_anvisa.setdefault(registro, []).append(equipamento)

    #for registro in reg_anvisa:
    #    print(f'Registro: {registro} tem {len(reg_anvisa[registro])} equipamentos')
    #print(f'Quantidade de registros:{len(reg_anvisa)}')
    gravarDicionario(reg_anvisa, 'relatorios/reg_anvisa.json')

    n_pesquisa = 0
    encontrado = 0
    relatorio_json = dict()

    for registro in reg_anvisa:
        for alerta in alertas_json:
            n_pesquisa += 1
            if 'Número de registro ANVISA:' in alertas_json[alerta] or 'Resumo' in alertas_json[alerta]:
                if alertas_json[alerta]['Número de registro ANVISA:'].find(registro) >= 0 or alertas_json[alerta]["Resumo:"].find(registro) >= 0:
                    encontrado += 1
                    if not registro in relatorio_json:
                        relatorio_json[registro] = {}
                        relatorio_json[registro]["Registro Anvisa"] = registro
                    if "Alertas encontrados" in relatorio_json[registro]:
                        relatorio_json[registro]["Alertas encontrados"] += 1
                    else:
                        relatorio_json[registro]["Alertas encontrados"] = 1
                    if not "Equipamentos" in relatorio_json:
                        relatorio_json[registro]["Equipamentos"] = reg_anvisa[registro].copy()
                    if not "Alertas" in relatorio_json[registro]:
                        relatorio_json[registro]["Alertas"] = []
                    relatorio_json[registro].setdefault("Alertas",[]).append(alertas_json[alerta])
                    print(f'Alerta encontrado: {alerta} -> Registro: {registro}')
                


        #print(f'Pesquisado: {i}. Encontrado: {encontrado}')
        #if encontrado > 0:
            #print(relatorio_json) 
    print(f'Pesquisado: {n_pesquisa}. Encontrado: {encontrado}')
    relatorio_json["Resumo pesquisa equipamentos"] = {}
    relatorio_json["Resumo pesquisa equipamentos"]["Pesquisados"] = n_pesquisa
    relatorio_json["Resumo pesquisa equipamentos"]["Encontrados"] = encontrado
    if type(dicio_adicionar) is dict:
        relatorio_json.update(dicio_adicionar)
    gravarDicionario(relatorio_json, nome_relatorio)  

logs = []

d = {'data-hora início': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

logger(d)

scrape_page(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),20)

relatorio_geral()

