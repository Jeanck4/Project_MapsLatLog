# importações do Python
import base64
import pdfkit
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import simplejson as json

path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'  # Altere para o caminho correto no seu sistema
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

# Importações de Bibliotecas Externas
from flask import Blueprint, request, jsonify, make_response, current_app
# Importações Internas
from utilitarios.funcoes_gerais import GeneralFuncs as g

mail_bp = Blueprint('mail', __name__)

@mail_bp.route("/mail", methods=['POST'])
def enviaEmail():
    json = request.get_json()
    print(json)
    pk_email = json.get('PK_EMAIL')
    pk_email = json.get('HTML_TO_PDF')   


    response = make_response(jsonify({"resultado": "Execução OK"}))
    response.status_code = 200
    return response 

@mail_bp.route("/converte-anexo/<conversao>", methods=['POST'])
def converteAnexo(conversao):
    
    json = request.get_json()
    print(json)

    response = make_response(jsonify({"resultado": "Conversão realizada!"}))
    response.status_code = 200
    return response

#-------------------------------------------------------------------------------------------------------------------
#ENVIO DE E-MAIL AUTOMATICO
#-------------------------------------------------------------------------------------------------------------------

@mail_bp.route("/processatemail", methods=['POST'])
def processatemail():
    try:
        jsonT = request.get_json()
        print(jsonT)
    except Exception as e:
        print(f'Erro ao ler o JSON: {e}')
        return make_response(jsonify({"erro": "Erro ao processar o JSON"}), 400)

    try:
        global conexao_db
        conexao_db = current_app.config['conexao_db']
        linhas = conexao_db.consulta_temail()  # Obtém todas as linhas
    except Exception as e:
        print(f'Erro ao consultar o banco de dados: {e}')
        return make_response(jsonify({"erro": "Erro ao consultar o banco de dados processatemail"}), 500)

    ip_smtp = '192.168.0.233'
    porta_smtp = '25'

    for linha in linhas:
        try:
            e_from = linha[0]
            e_to = linha[1]
            subject = linha[2]
            body = linha[3]
            text_html = linha[4]
            status = linha[5]
            documento = linha[6].read()  # Leitura do BLOB como bytes

            # Salvar o conteúdo do BLOB em um arquivo HTML temporário
            with open("temp_documento.html", "wb") as temp_html_file:
                temp_html_file.write(documento)

                options = {
                    'quiet': '',  # Suprime a saída padrão do wkhtmltopdf
                    'page-size': 'A3',  # Tamanho da página A3
                    'encoding': "UTF-8",  # Codificação do arquivo
                    'no-outline': None  # Remove o contorno ao redor do PDF
                }

            # Convertendo o documento HTML para PDF usando pdfkit
            pdf_content = pdfkit.from_file("temp_documento.html", False, configuration=config, options=options)

            # Preparar dados do e-mail
            email_data = {
                "remetente": e_from,
                "destinatário": e_to,
                "assunto": subject,
                "corpo": body,
                "anexo": pdf_content  # Usando o conteúdo do PDF gerado como anexo
            }

            # Conectar ao servidor SMTP
            conexao_smtp = conectar_banco_SMTP(ip_smtp, porta_smtp)

            # Enviar o email
            enviar_email(conexao_smtp, email_data)

            # Encerrar a conexão SMTP
            conexao_smtp.quit()

            # Atualizar o status do email
            conexao_db.atualiza_status(e_from, e_to, subject)

        except Exception as e:
            print(f'Erro ao enviar o email: {e}')
            return make_response(jsonify({"erro": "Erro ao enviar o email"}), 500)


    response = make_response(jsonify({"resultado": "Emails enviados com sucesso!"}))
    response.status_code = 200
    return response

def conectar_banco_SMTP(ip_smtp, porta_smtp):
    try:
        # Configuração do servidor SMTP
        server = smtplib.SMTP(ip_smtp, porta_smtp)
        server.ehlo()
        print(f'Conexão ao servidor SMTP {ip_smtp}:{porta_smtp} bem-sucedida.')
        return server
    except Exception as e:
        print(f'Erro ao conectar ao servidor SMTP: {e}')
        raise

def enviar_email(server, email_data):
    try:
        email_de = email_data["remetente"]
        email_para = email_data["destinatário"]
        assunto = email_data["assunto"]
        corpo = email_data["corpo"]
        arquivo_anexo = email_data["anexo"]

        # Montar o email
        msg = MIMEMultipart()
        msg['From'] = email_de
        msg['To'] = email_para
        msg['Subject'] = assunto

        # Adicionar corpo do email
        mensagem_corpo = MIMEText(corpo, 'plain')
        msg.attach(mensagem_corpo)

        # Adicionar anexo
        part = MIMEApplication(arquivo_anexo, Name='anexo.pdf')
        part['Content-Disposition'] = 'attachment; filename="anexo.pdf"'
        msg.attach(part)

        # Enviar email
        server.sendmail(email_de, email_para, msg.as_string())
        print("Email enviado com sucesso.")

    except Exception as e:
        print(f'Erro ao enviar o email: {e}')
        raise
