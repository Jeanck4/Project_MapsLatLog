# Importações de Bibliotecas Externas
from flask import Blueprint, request, redirect, make_response, jsonify, render_template
#from flask_login import login_user, logout_user, current_user, login_required


from utilitarios.funcoes_gerais import GeneralFuncs as g

panel_bp = Blueprint('panel', __name__)

@panel_bp.route("/painel", methods=['GET'])
def painel():
    return render_template("painel.html")

@panel_bp.route("/loginpainel", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        print(f"Usuário: {usuario} senha: {senha}")
        return render_template("painel.html")
    else:
        print("else")
        return render_template("login.html")