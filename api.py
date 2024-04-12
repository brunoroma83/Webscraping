#versão que funciona no pythonanywhere.com
from flask import Flask, request
import pandas as pd
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <html><head></head><body><pre>
    Bem-Vindo a API de consulta de alerta por registro ANVISA!

    Exemplos de consultas:
    https://brunoroma.pythonanywhere.com/alerta/4361
    https://brunoroma.pythonanywhere.com/registro/80146502070

    by Bruno Roma - contato@brunoroma.eng.br

    Para automatizar a consulta de alertas no Excel:

    Você pode usar essa função da seguinte maneira:

    1. Na planilha do Excel, insira o número do registro em uma célula, por exemplo, A1.
    2. Em outra célula, digite `=ConsultarAPI(A1)` para chamar a função e passar o valor da célula A1 como parâmetro.
    3. Pressione Enter para obter o resultado da API na célula.

    Certifique-se de que o formato do registro esteja correto para ser usado na URL da API. Se a API esperar um formato diferente, você pode precisar ajustar o código conforme necessário.

código vba
Function ConsultarAPI(registro As String) As String
    Dim req As Object
    Dim url As String
    Dim resposta As String
    
    ' Concatenar o registro com a URL base
    url = "https://brunoroma.pythonanywhere.com/registro/" & registro
    
    ' Criar um objeto para realizar a solicitação à API
    Set req = CreateObject("MSXML2.XMLHTTP")
    
    ' Fazer a solicitação GET à API
    req.Open "GET", url, False
    req.send
    
    ' Armazenar a resposta da API
    resposta = req.responseText
    
    ' Retornar a resposta da API
    ConsultarAPI = resposta
End Function

    </pre></body></html>
    """

@app.route('/registro/<registro>', methods=['GET'])
def registro(registro):
    df_reg = pd.read_json('/home/brunoroma/Webscraping/reg_anvisa_alerta.json')
    info = dict()
    info["IP"]=request.remote_addr
    info["args"]=request.args
    #print(df_reg.value_counts('Número de registro ANVISA'))
    df_reg_filtrado = df_reg.loc[df_reg['Número de registro ANVISA'].isin([registro])]
    #return df_reg_filtrado
    if df_reg_filtrado.empty: 
        resposta = f'Nenhum alerta encontrado para {registro}'
        info["resposta"] = resposta        
    else: 
        resposta = f'Alerta(s): {df_reg_filtrado["Alerta"].values}'
    logger(info)
    return resposta

@app.route('/resumo', methods=['GET'])
def alerta2():
    df_reg = pd.read_json('/home/brunoroma/Webscraping/reg_anvisa_alerta.json')
    return f"""
    <pre>
    Alerta Info
    {df_reg}

    Último alerta registrado: {df_reg['Alerta'].max()}

    Top 20 registros:
    {df_reg.value_counts('Número de registro ANVISA').head(20)}
    </pre>
    """

@app.route('/alerta/<alerta>', methods=['GET'])
def alerta(alerta):
    df_reg = pd.read_json('/home/brunoroma/Webscraping/reg_anvisa_alerta.json')
    df_reg_filtrado = df_reg.loc[df_reg['Alerta'].isin([int(alerta)])]
    if df_reg_filtrado.empty: return {'erro': f'Nenhum alerta encontrado para {alerta}'}
    else: return(df_reg_filtrado.to_dict())

def logger(dados, nome_arquivo='/home/brunoroma/Webscraping/log_api.json'):
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
