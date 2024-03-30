import pandas as pd
import os
from dotenv import dotenv_values

envs = dotenv_values('.env')

df = pd.read_json('reg_anvisa_alerta.json')
#print(df.info)
print(df['Alerta'].max())
print(df.value_counts('Número de registro ANVISA'))
print(f'gemini = {envs["GEMINI_API_KEY"]}')