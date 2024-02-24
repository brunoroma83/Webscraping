import webscraping as wb
import matplotlib.pyplot as plt

def contar_numeros(dicionario):
  numeros = {}
  empresas = {}
  alertas = {}
  
  for alerta, valor in dicionario.items():
    
    if 'Empresa:' in valor: empresa = valor['Empresa:']
    if 'Número de registro ANVISA:' in valor:
        reg_anvisa = valor['Número de registro ANVISA:'].split(";")
        reg_anvisa_limpos = [numero.strip() for numero in reg_anvisa]
        #print(f'alerta={alerta} reg_anvisa={reg_anvisa_limpos}')
    
    
    for palavra in reg_anvisa_limpos:
        if len(palavra) == 11 and palavra.isdigit():
            # Contabiliza a ocorrência do número
            numeros[palavra] = numeros.get(palavra, 0) + 1
            empresas[empresa] = empresas.get(empresa, 0) + 1
            if not empresa in alertas: alertas[empresa] = []
            alertas[empresa].append(alerta)
            
# Ordena o dicionário por valor (do maior para o menor)
  numeros_ordenados = sorted(numeros.items(), key=lambda x: x[1], reverse=True)
  wb.gravarDicionario(numeros_ordenados,'estatisticas/numeros_ordenados.json')
  empresas_ordenado = sorted(empresas.items(), key=lambda x: x[1], reverse=True)
  wb.gravarDicionario(empresas_ordenado,'estatisticas/empresas.json')

  # Imprime o dicionário ordenado
  print(f'Alertas na base: {len(dicionario.keys())}')
  print(f'Registros ANVISA: {len(numeros.keys())}')
  print(f'Empresas: {len(empresas.keys())}')
  print("Top 10 Registros ANVISA:")
  for i, (chave, valor) in enumerate(numeros_ordenados):
    if i == 10: break
    print(f"{valor} : {chave}")              
  
  print("Top 10 Empresas:")
  for i, (chave, valor) in enumerate(empresas_ordenado):
    if i == 10: break
    print(f"{valor} : {chave}")              
  
  return numeros

def gerar_grafico(numeros_contados):

    # Gera o gráfico
    plt.bar(numeros_contados.keys(), numeros_contados.values())
    plt.xlabel("Número")
    plt.ylabel("Ocorrências")
    plt.title("Distribuição de Números de 11 Dígitos")
    plt.show()

dicionario = wb.carregar_json('dicionario.json')
numeros_contados = contar_numeros(dicionario)
wb.gravarDicionario(numeros_contados,'estatisticas/aparicao_reg_anvisa.json')

#removendo valores menores que 4 para apresentar no gráfico
para_grafico = {}
for chave, valor in numeros_contados.items():
    if valor < 3: continue
    para_grafico[chave] = valor
    #if valor > 6: print(f'>6 {chave} -> {valor}')

# Gera o relatório CSV da contagem de registros
gerar_grafico(para_grafico)