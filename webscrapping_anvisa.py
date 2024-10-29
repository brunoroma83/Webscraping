from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import pandas as pd
import schedule, ssl, requests, smtplib, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import google.generativeai as genai

load_dotenv()

url = "https://www.gov.br/anvisa/pt-br/assuntos/noticias-anvisa"
num_days = 1  # Número de dias para buscar as notícias

def extract_news(url, num_days, filename):
    # Fazendo a requisição HTTP para o site
    response = requests.get(url)

    # Verificando se a requisição foi bem-sucedida
    if response.status_code == 200:
        # Parseando o conteúdo HTML da página
        soup = BeautifulSoup(response.content, 'html.parser')

        # Encontrando as seções que contêm as notícias
        noticias = soup.find_all('ul', class_='noticias')  # Todas as notícias
        noticias_li = noticias[0].find_all('li')

        # Obtendo a data de hoje
        today = datetime.now()

        # Initialize an empty list to store the extracted data
        data = []

        # carregar arquivo anvisa.csv em um dataframe
        # veriricar se o arquivo anvisa.csv exite e se não está vazio

        if os.path.exists('anvisa.csv') and os.path.getsize('anvisa.csv') > 0:
            df_anvisa = pd.read_csv('anvisa.csv')
        else:
            df_anvisa = pd.DataFrame(columns=['Data', 'Título', 'Descrição', 'Link', 'Classificação'])
        

        for noticia in noticias_li:

            link = noticia.find('a')['href']

            #verifica se o link da notícia já existe no dataframe df_anvisa
            if link in df_anvisa['Link'].values:
                #print(f"Notícia {link} já existe no dataframe df_anvisa.")
                continue

            titulo = noticia.find('h2').get_text().strip()
            data_noticia = noticia.find('span', class_='data').get_text().strip()
            span_desc = noticia.find_all('span', class_='descricao')


            # Convertendo a data da notícia para um objeto datetime
            data_noticia_datetime = datetime.strptime(data_noticia, '%d/%m/%Y')

            # Verificando se a notícia foi publicada nos últimos x dias
            if (today - data_noticia_datetime).days <= num_days:
                # Extracting the description
                for span in span_desc:
                    desc = span.get_text().split('-', 1)[1].strip()  # Split at the first '-'
                    break
                
                GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
                genai.configure(api_key=GOOGLE_API_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')

                # classificar notícia usando API Gemini
                prompt = f"""
                Classifique o texto a seguir conforme os exemplos. 
                Exemplo: Anvisa participa da Cúpula Global de Ciência Regulatória - Em sua 14ª edição, a conferência anual foi sediada pela US Food and Drug Administration - FDA, e teve como tema a transformação digital em ciência regulatória.
                Classificação: Evento Internacional, FDA, Transformação Digital

                Exemplo: Participe do webinar sobre atualizações no formulário de registro de cosméticos - Encontro virtual será no dia 24/9, às 10h. Participe!
                Classificação: Convite, Evento online, Registro de cosméticos

                Exemplo: Anvisa cria Câmara Técnica de Pesquisa Clínica de Medicamentos e Dispositivos Médicos - Com a Catepec, a Agência aprimora e consolida a participação social e científica nos processos de regulamentação e avaliação de pesquisas clínicas de medicamentos e dispositivos médicos.
                Classificação: Dispositivos Médicos, Pesquisa Clinica, Regulamentação, Medicamentos

                Texto: {titulo} - {desc}

                Na sua resposta deve conter apenas a classificação, nenhum outro texto.
                """
                try:
                    response = model.generate_content(prompt)
                    #print("Resposta IA: ",response)
                    classification = response.text.strip('\n')
                except Exception as e:
                    print(f"Erro ao classificar noticia: {str(e)}")
                    classification = "Não classificado"
                print("Classificação: ",classification)
                # Append the extracted data to the list
                data.append([data_noticia, titulo, desc, link, classification])

        # verifica se data está vazio, se verdadeiro return None
        if not data:
            return None
        # Create a pandas DataFrame from the extracted data
        df = pd.DataFrame(data, columns=['Data', 'Título', 'Descrição', 'Link', 'Classificação'])
        # concatenar df e df_anvisa antes de salvar para arquivo
        df_concat = pd.concat([df, df_anvisa], ignore_index=True)
        df_concat.to_csv(f"{filename}.csv", index=False)
        return df
    else:
        print(f"Erro ao acessar o site. Status code: {response.status_code}")
        return None

def strip_list(n):
    return [x.strip() for x in n]

def job():
    print("Running the news extraction job...")
    df = extract_news(url, num_days, "anvisa")

    if df is not None:
        # Convert the DataFrame to a string for the email body
        df_str = df.to_html(index=False)
        
        #print(f"enviar email. df: {df_str}")

        # Send the email
        subject = "ANVISA News Extraction"
        body = f"Here are the latest ANVISA news:<br><br>{df_str}"
        to_email = "bruuno@gmail.com"
        send_email(subject, body, to_email)
    else:
        print("No news found.")

# Schedule the job to run every day at 9 am
schedule.every().day.at("09:00").do(job)

def send_email(subject, body, to_email):
    # Set up the email parameters
    email_from = "site@nucleoec.ong.br"
    email_password = os.getenv('SENHA_EMAIL')

    # Create the email message
    msg = MIMEMultipart("alternative")
    part2 = MIMEText(body, "html")
    msg.attach(part2)
    msg['Subject'] = subject
    msg['From'] = email_from
    msg['To'] = to_email

    # Connect to the email server and send the email
    try:
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL('smtp.hostinger.com', 465, context=context)
        server.login(email_from, email_password)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {str(e)}")

# Testando a função
job()

# Keep the script running until manually stopped
#while True:
#    schedule.run_pending()
#    time.sleep(30)