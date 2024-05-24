# importações do Python

# Importações de Bibliotecas Externas
from flask import Blueprint, jsonify, make_response
# Importações Internas

main_bp = Blueprint('main', __name__)

@main_bp.route("/", methods=['GET'])
def index():
    #return "<h1>Teste</h1>"
    return make_response(jsonify({"resultado": "API ONLINE"}))

