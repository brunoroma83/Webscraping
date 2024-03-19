from flask import Flask
import pandas as pd
from ws_funcoes import buscar_registro_anvisa

app = Flask(__name__)

alertas = pd.read_json('reg_anvisa_alerta.json')

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/registro/<registro>', methods=['GET'])
def registro(registro):
    return buscar_registro_anvisa([registro]).to_dict()

if __name__ == '__main__':
   app.run(port=5000)