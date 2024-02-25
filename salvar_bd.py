import bancodedados as bd
from webscraping import carregar_json
import pandas as pd

alertas = carregar_json('dicionario.json')
bd.salvar_alertas(alertas)

equipamentos = carregar_json('equipamentos.json')
bd.salvar_equipamentos(equipamentos)

#pesquisar registro anvisa no banco de dados
print(bd.perquisar('alertas','Número de registro ANVISA:','80146502242'))