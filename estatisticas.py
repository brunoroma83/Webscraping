# apresentar a quantidade de alertas no arquivo
# apresentar as 10 empresas com maior quantidade de alertas
# apresentar o equipamento ou registro anvisa com maior quantidade de alertas


import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_json('dicionario.json')

print(f'Alertas: {df['Alerta'].count()}')
empresas = df.value_counts('Empresa')
print(empresas.head(10))
nome_tecnico = df.value_counts('Nome Técnico')
print(nome_tecnico)


def gerar_grafico(numeros_contados):

    # Gera o gráfico
    plt.bar(numeros_contados.keys(), numeros_contados.values())
    plt.xlabel("Número")
    plt.ylabel("Ocorrências")
    plt.title("Distribuição de Números de 11 Dígitos")
    plt.show()
