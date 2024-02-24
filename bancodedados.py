import sqlite3

def salvar_alertas(dicionario):
    conn = sqlite3.connect('webscraping.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertas(
                   'Número do alerta:' text,
                   'Data do alerta:' text,
                   'Link do alerta:' text,
                   'Resumo:' text,
                   'Identificação do produto ou caso:' text,
                   'Problema:' text,
                   'Ação:' text,
                   'Histórico:' text,
                   'Recomendações:' text,
                   'Anexos:' text,
                   'Informações Complementares:' text,
                   'Empresa:' text,
                   'Nome Comercial:' text,
                   'Nome Técnico:' text,
                   'Número de registro ANVISA:' text,
                   'Tipo de produto:' text,
                   'Classe de Risco:' text,
                   'Modelo afetado:' text,
                   'Números de série afetados:' text)
    """)

    for chave, valor in dicionario.items():
        valores = []
        valores = list(valor.values())
        if len(valores) == 19: cursor.execute("INSERT INTO alertas VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", valores)
    conn.commit()