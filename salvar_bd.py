import bancodedados as bd
import pandas as pd

alertas = pd.read_json('dicionario.json')
bd.salvar_alertas(alertas.to_dict('records'))

equipamentos = pd.read_json('equipamentos.json')
bd.salvar_equipamentos(equipamentos.to_dict('records'))

#pesquisar registro anvisa no banco de dados
print(bd.perquisar('alertas','Número de registro ANVISA','80146502242'))