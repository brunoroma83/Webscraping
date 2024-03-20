#versão que funciona no pythonanywhere.com
from flask import Flask
import pandas as pd

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
    </pre></body></html>
    """

@app.route('/registro/<registro>', methods=['GET'])
def registro(registro):
    df_reg = pd.read_json('/home/brunoroma/Webscraping/reg_anvisa_alerta.json')

    #print(df_reg.value_counts('Número de registro ANVISA'))
    df_reg_filtrado = df_reg.loc[df_reg['Número de registro ANVISA'].isin([registro])]
    #return df_reg_filtrado
    if df_reg_filtrado.empty: return {'erro': f'Nenhum alerta encontrado para {registro}'}
    else: return(df_reg_filtrado.to_dict())