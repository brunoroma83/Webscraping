# integrar o gemini no webscraping, inicialmente para encontrar algumas informações da extração do html, como por exemplo o nome da empresa.

from dotenv import dotenv_values
import google.generativeai as genai
import pandas as pd

# iniciando Gemini AI API
envs = dotenv_values('.env')
genai.configure(api_key=envs["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

#carregar dicionario
#df = pd.read_json('dicionario.json')
#dicio = df.to_dict('records')

response = model.generate_content(f"Qual a capital do Brasil?")
print(response.prompt_feedback)
print(response.text)