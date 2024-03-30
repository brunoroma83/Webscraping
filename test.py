import pandas as pd

df = pd.read_json('reg_anvisa_alerta.json')
#print(df.info)
print(df['Alerta'].max())
print(df.value_counts('Número de registro ANVISA'))