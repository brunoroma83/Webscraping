import pandas as pd

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
    df_reg.to_json('reg_anvisa_alerta.json')
    return df_reg

def buscar_registro_anvisa(registro_anvisa):
    df_reg = separar_alertas()
    #print(df_reg.value_counts('Número de registro ANVISA'))
    df_reg_filtrado = df_reg.loc[df_reg['Número de registro ANVISA'].isin(registro_anvisa)]
    #return df_reg_filtrado
    if df_reg_filtrado.empty: return pd.DataFrame({'erro': f'Nenhum alerta encontrado para {registro_anvisa}'}, index=[0])
    else: return(df_reg_filtrado)

# passar números de registo em formato de lista
#list_reg = [str(x) for x in range(80158990001,80158990100) if x > 0]
#list_reg = ['95217UN18']
#resultado = buscar_registro_anvisa(list_reg)

