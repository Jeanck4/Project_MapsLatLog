# importações do Python
import base64
# Importações de Bibliotecas Externas
from flask import Blueprint, request, jsonify, make_response, current_app
# Importações Internas
from utilitarios.funcoes_gerais import GeneralFuncs as g

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/auth", methods=['POST'])
def autenticaBanco():
    g.grava_log(mensagem='Chamada da rota de login...', modulo=__file__)
    resultado = "Erro ao identificar dados de autenticação"

    if 'Authorization' in request.headers:
        #Pega o Header da requisição
        auth_header = request.headers['Authorization']
        #Retira o "Basic" do header
        try:
            credentials = auth_header.split(' ')[1]
        except:
            credentials = auth_header
        
        #Converte de base64 para utf-8
        decoded_credentials = base64.b64decode(credentials).decode('utf-8')

        username, password   = decoded_credentials.split(':')
        
        #Instanciando a conexao_db como global para ser acessível à outros métodos
        global conexao_db
        conexao_db = current_app.config['conexao_db']
        conexao_db.login(salvar=0,user=username,passw=password)
        resultado = conexao_db.resultado

    response = make_response(jsonify({"resultado": resultado}))
    response.status_code = conexao_db.status
    return response    

@auth_bp.route("/logout", methods=['POST'])
def logoutBanco():
    #resultado = "Logout efetuado com sucesso!"
    g.grava_log(mensagem='Chamada da rota de logout...', modulo=__file__)
    resultado = "Usuário desconectado!"
    if 'conexao_db' in globals():
        if conexao_db is not None:
            conexao_db.logout()
            resultado = conexao_db.resultado

    return jsonify({"resultado": resultado})