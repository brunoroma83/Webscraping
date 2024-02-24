import webscraping as ws
import bancodedados as bd

alertas = ws.carregar_json('dicionario.json')
bd.salvar_alertas(alertas)
