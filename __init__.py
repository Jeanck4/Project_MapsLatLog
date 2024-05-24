"""
Este módulo armazena a chamada principal da automação. 
"""
# importações do Python
import socket
# Importações de Bibliotecas Externas
from flask import Flask
#from flask_login import LoginManager

# Importações Internas
from .routes import main_bp, auth_bp, exec_bp, panel_bp, function_bp, mail_bp
from .controllers.execucoes_db import ConexaoBanco

def create_app():
    app = Flask(__name__)
    #login_manager = LoginManager(app)
    
    # Registrar blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(exec_bp)
    app.register_blueprint(panel_bp)
    app.register_blueprint(function_bp)
    app.register_blueprint(mail_bp)

    app.config['hostname'] = socket.getfqdn().split('.')[0].lower()

    if socket.getfqdn() == "CTVPOMAP42.cativa.com.br" or socket.getfqdn() == "CTVPOMAP48.cativa.com.br":
        app.config['prod_hml'] = 'prod'
    else:
        app.config['prod_hml'] = 'hml'

    # Conexão com o Banco
    conexao_db = ConexaoBanco()
    app.config['conexao_db'] = conexao_db

    return app