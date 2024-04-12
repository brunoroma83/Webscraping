import pandas as pd

df = pd.read_json('reg_anvisa_alerta.json')
registro = "80146502070"
df_reg_filtrado = df.loc[df['Número de registro ANVISA'].isin([registro])]
print(df_reg_filtrado["Alerta"].values)