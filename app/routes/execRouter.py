# importações do Python
import importlib
import os
import socket
import sys
# Importações de Bibliotecas Externas
from flask import Blueprint, request, jsonify, make_response, current_app
import cx_Oracle
# Importações Internas
from utilitarios.funcoes_gerais import GeneralFuncs as g
...

exec_bp = Blueprint('executar', __name__)
modulo_log = "EXECROUTER"

@exec_bp.route("/executar/<modulo>", methods=['POST'])
def executar_automacao(modulo):
    g.grava_log(mensagem='Iniciando execução da rota...', modulo=__file__)

    g.grava_log(mensagem=f'Módulo da rota: {modulo}', modulo=__file__)

    global conexao_db
    conexao_db = current_app.config['conexao_db']
    g.grava_log(mensagem='Buscou instância da conexão',modulo=__file__)
    if 'conexao_db' not in globals():
        g.grava_log(mensagem='Conexão com o banco não foi estabelecida',modulo=__file__)
        response = "Conexão com o banco não estabelecida!"
    else:
        try:
            if (conexao_db.esta_conectado()):
                # Busca pela automação da requisição
                arquivo = 'automacao_' + modulo
                dir_atual = os.path.dirname(os.path.abspath(__file__))
                dir_automacoes = os.path.join(dir_atual, '..', '..', 'engine', arquivo + '.py')
                g.grava_log(mensagem=f'Diretório da automação: {dir_automacoes}',modulo=__file__)
                
                if os.path.exists(dir_automacoes):
                    g.grava_log(mensagem='Encontrou a automação',modulo=__file__)
                    #Insere registro de inicio da Execucao(retorna pk)
                    pk_controle_execucao = conexao_db.inicia_execucao(arquivo)
                    if g.is_none_null(pk_controle_execucao):
                        g.grava_log(mensagem='Erro ao iniciar o controle de Execução',modulo=__file__)
                        response = make_response(jsonify({"resultado": "Erro ao iniciar o controle de Execução!"}))
                        response.status_code = 404
                        return response
                    
                    g.grava_log(mensagem=f'pk_controle_execucao {pk_controle_execucao}',modulo=__file__)
                    json = request.get_json()
                    lib_modulo = importlib.import_module("engine." + arquivo)
                    
                    g.grava_log(mensagem='Buscando Main() da automação',modulo=__file__)
                    automacao = lib_modulo.Main()
                    # Encerra os processos existentes
                    g.grava_log(mensagem='Encerrando processos do chrome',modulo=__file__)
                    if socket.getfqdn() == "CTVPOMAP42.cativa.com.br" or socket.getfqdn() == "CTVPOMAP46.cativa.com.br":
                        os.system("taskkill /f /im chrome.exe")
                        os.system("taskkill /f /im chromedriver.exe")
                    # Inicia a execução
                    g.grava_log(mensagem='Iniciando execução da automacao.main()',modulo=__file__)
                    automacao.main(json)
                    response = automacao.response
                    response.status_code = automacao.response.status
                    if response.status_code == 200:
                        status_execucao = 'F'
                    else:
                        status_execucao = 'E'
                    g.grava_log(mensagem='Parando execução',modulo=__file__)
                    deu_certo = conexao_db.para_execucao(pk_controle_execucao, status_execucao)
                    if not deu_certo:
                        g.grava_log(mensagem='Erro ao encerrar o controle de execução!',modulo=__file__)
                        response_data = {
                            "resultado": response.get_json()["resultado"] + ["Erro ao finalizar Controle de Execução!"]
                        }

                        response = make_response(jsonify(response_data), 500)
                else:
                    # Se chegou aqui, a automação não foi encontrada
                    response = make_response(jsonify({"resultado": "Automação não localizada!"}))
                    response.status_code = 404
            else:
                response = make_response(jsonify({"resultado": "Usuário não autenticado!"}))
                response.status_code = 401
        except cx_Oracle.DatabaseError as erro:
            if not g.is_none_null(pk_controle_execucao):
                conexao_db.para_execucao(pk_controle_execucao, 'E') 
            g.grava_log(mensagem=f'DatabaseError: {erro}',modulo=__file__)
            response = "Erro ao se comunicar com o banco."
        except cx_Oracle.InterfaceError as erro:
            if not g.is_none_null(pk_controle_execucao):
                conexao_db.para_execucao(pk_controle_execucao, 'E') 
            g.grava_log(mensagem=f'InterfaceError: {erro}',modulo=__file__)
            response = "Erro ao se comunicar com o banco."
        except AttributeError as e:
            if not g.is_none_null(pk_controle_execucao):
                conexao_db.para_execucao(pk_controle_execucao, 'E') 
            g.grava_log(mensagem=f'AttributeError: {e}',modulo=__file__)
            response = f"Erro de atributo: {e}"
        except Exception as e:
            if not g.is_none_null(pk_controle_execucao):
                conexao_db.para_execucao(pk_controle_execucao, 'E') 
            g.grava_log(mensagem=f'Exception: {e}',modulo=__file__)
            response = f"Erro não catalogado: {e}"
        except:
            if not g.is_none_null(pk_controle_execucao):
                conexao_db.para_execucao(pk_controle_execucao, 'E') 
            g.grava_log(mensagem=f'Exception: {e}', modulo=__file__)
            response = f"Exception não tratada"

    """for key in list(sys.modules.keys()):
        if key != '__main__':
            del sys.modules[key]

    # Limpa arquivos de cache pyc
    for root, dirs, files in os.walk(sys.path[0]):
        for file in files:
            if file.endswith('.pyc') or file.endswith('.pyo'):
                try:
                    os.remove(os.path.join(root, file))
                   # print(f'Excluiu root {root} file {file}')
                except:
                    ...
                   # print(f'Não excluiu root {root} file {file}')"""

    return response 