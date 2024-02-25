import sqlite3

def salvar_alertas(dicionario):
    conn = sqlite3.connect('webscraping.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertas(
                   'Número do alerta:' INTEGER NOT NULL PRIMARY KEY,
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
        if len(valores) == 19: cursor.execute("INSERT OR IGNORE INTO alertas VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", valores)
    conn.commit()

def salvar_equipamentos(dicionario):
    conn = sqlite3.connect('webscraping.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipamentos(
        "ID" TEXT NOT NULL PRIMARY KEY,
        "Tipo" TEXT,
        "Marca" TEXT,
        "Modelo" TEXT,
        "Série" TEXT,
        "TAG" TEXT,
        "Lote" TEXT,
        "Patrimônio" TEXT,
        "Unidade" TEXT,
        "Setor" TEXT,
        "Localização" TEXT,
        "Propriedade" TEXT,
        "Garantia início" TEXT,
        "Garantia término" TEXT,
        "Número Registro Anvisa" TEXT,
        "Situação do Registro Anvisa" TEXT,
        "Data vigência" TEXT,
        "Classificação de Risco" TEXT,
        "Situação" TEXT,
        "Foto" TEXT,
        "Contrato" TEXT,
        "Data inclusão" TEXT)
    ''')
    #22 COLUNAS
    
    for valor in dicionario:
        valores = []
        valores = list(valor.values())
        if len(valores) == 22: cursor.execute("INSERT OR IGNORE INTO equipamentos VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", valores)
    conn.commit()

def perquisar(tabela,chave,valor):
    conn = sqlite3.connect('webscraping.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {tabela} WHERE "{chave}" = "{valor}"')
    return cursor.fetchall()