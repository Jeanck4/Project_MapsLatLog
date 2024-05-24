# importações do Python
from time import sleep
import socket

# Importações de Bibliotecas Externas
import cx_Oracle

# Importações Internas 
from app.utils.constants import DATABASE, DATABASE_HML
from utilitarios.funcoes_gerais import GeneralFuncs as g
from flask import jsonify, make_response, current_app

class ConexaoBanco:
    def __init__(self):
        if socket.getfqdn() == "CTVPOMAP42.cativa.com.br" or socket.getfqdn() == "CTVPOMAP48.cativa.com.br":
            self.host = DATABASE['db_host']
            self.sid = DATABASE['db_sid']
        else:
            self.host = DATABASE_HML['db_host']
            self.sid = DATABASE_HML['db_sid']
        
        g.grava_log(mensagem=f"Servidor do banco definido como Host: {self.host} | SID: {self.sid}",modulo=__file__)

        self.port = 1521
        self.resultado = 'Inicializado!'
        self.status = 200

    def busca_proxima_pk(self, nm_sequence):
        if g.is_none_null(nm_sequence):
            return 
        try:
            sql = f"select rpacativa.{nm_sequence} from dual"

            cursor = self.connection.cursor()
            cursor.execute(sql)
       
            # Recupere os resultados da consulta
            for linha in cursor:
                pk_controle_execucao = linha[0]

            cursor.close()
            
        except:
            return False

        return pk_controle_execucao 
    
    def inicia_execucao(self, nm_arquivo):
        if g.is_none_null(nm_arquivo):
            return None
        try:                      
            pk_controle_execucao = self.busca_proxima_pk('seq_controle_execucao.nextval')
            
            sql = f"insert into rpacativa.controle_execucao (pk_controle_execucao, nm_arquivo_py, cd_status, ds_host) values ({pk_controle_execucao},'{nm_arquivo}','P', '{current_app.config['hostname']}')"
            print(sql)
            cursor = self.connection.cursor()
            cursor.execute(sql)
            
            self.connection.commit()
             
            # Teste recursivamente se o processo pode ser executado
            deu_boa = self.controle_execucao(pk_controle_execucao)

            # Quando chegar a vez de executar, atualiza para 'T' (em execução)
            sql = f"update rpacativa.controle_execucao set cd_status = 'T', dt_inicio = sysdate where pk_controle_execucao = {pk_controle_execucao}"
            cursor = self.connection.cursor()
            cursor.execute(sql)
            
            self.connection.commit()
        except:
            return None

        return pk_controle_execucao
    
    def para_execucao(self, pk_controle_execucao, status):
        if g.is_none_null(pk_controle_execucao):
            return False
        try:
            sql = f"update rpacativa.controle_execucao set cd_status = '{status}', dt_fim = sysdate where pk_controle_execucao = {pk_controle_execucao}"
            cursor = self.connection.cursor()
            cursor.execute(sql)
            
            self.connection.commit()
        except Exception as e:
            return False
        return  True
    
    def controle_execucao(self, pk_controle_execucao):
        try:

            while self.proxima_execucao() != pk_controle_execucao:
                sleep(5)

            return True
        except:
            return False

    
    def proxima_execucao(self):
        try:
            sql = f"select * from rpacativa.v_proxima_execucao where ds_host = '{current_app.config['hostname']}'"
            cursor = self.connection.cursor()
            cursor.execute(sql)

            for linha in cursor:
                proxima = linha[0]

            print(f'proxima pk: {proxima}')
            return proxima
        except:
            return 0

    
    def login(self, salvar=int, user=str, passw=str):
        try:
            if (self.esta_conectado()):
                self.resultado = "Usuário já autenticado!"
                self.status = 200
            else:
                self.__autentica(salvar, user, passw)
        except:
            self.__autentica(salvar, user, passw)
    
    def __autentica(self, salvar=int, user=str, passw=str):
            g.grava_log(mensagem=f"Iniciando tentativa de login com usuário {user}",modulo=__file__)
            self.resultado = 'Erro na autenticação!'
            self.status = 401

            # Crie a string de conexão DSN
            self.dsn = cx_Oracle.makedsn(self.host, self.port, self.sid)
            if salvar != 1:
                self.usuario_db = user
                self.senha_db = passw
                try:
                    # Conecta ao Banco
                    self.connection = cx_Oracle.connect(self.usuario_db, self.senha_db, self.dsn)
                    g.grava_log(mensagem=f"Conexão com o banco estabelecida!",modulo=__file__)
                    self.resultado = 'Conectado!'
                    salvar = 1
                    self.status = 200

                except Exception as error:
                    # Login inválido!
                    g.grava_log(mensagem=f"Erro ao autenticar usuário {user}!",tipo="ERROR",modulo=__file__)
                    self.resultado = "Usuário não autenticado!"
                    print(error)
                if salvar == 1:
                    print("\033[32mLogin Efetuado com sucesso!\033[0m")

    def logout(self):
        g.grava_log(mensagem=f"Iniciando tentativa de logout!",modulo=__file__)
        if (self.esta_conectado()):
            try: 
                self.connection.close()
                g.grava_log(mensagem=f"Usuário desconectado!",modulo=__file__)
                self.resultado = "Usuário desconectado!"
            except Exception as e:
                g.grava_log(mensagem=f"Exception ao tentar realizar logout!",tipo="ERROR",modulo=__file__)
                self.resultado = "Erro inserperado: " + e
        else:
            g.grava_log(mensagem=f"Sem sessão estabelecida. Não houve necessidade de realizar logout!",modulo=__file__)
    
    def credenciais(self, cd_credencial):
        """Retorna as credencias solicitadas"""
        g.grava_log(mensagem=f"Buscando credencial {cd_credencial}!",modulo=__file__)
        # Crie um cursor para executar consultas
        cursor = self.connection.cursor()

        # Executa consultas SQL usando o cursor
        sql = f"SELECT DS_USUARIO, DS_SENHA, DS_URL, DS_DIRETORIO FROM RPACATIVA.CREDENCIAL WHERE CD_CREDENCIAL = '{cd_credencial}'"
        cursor.execute(sql)

        # Recupere os resultados da consulta
        for linha in cursor:
            coluna = linha
            usuario = coluna[0]
            senha = coluna[1]
            url = coluna[2]
            diretorio = coluna[3]

        cursor.close()
        g.grava_log(mensagem=f"Credencial encontrada e retornada!",modulo=__file__)
        return usuario, senha, url, diretorio

    def lista_relatorios(self, cd_workspace, cd_relatorio):
        """ Retorna os relatórios que devem ser atualizados"""

        def blacklist(entrada):
            #A validação já foi feita anteriormente, aqui apenas evitamos a exception para quando for informado somente o workspace
            if entrada is None:
                return False
            # Lista de caracteres e sequência de caracteres à tratar
            blacklist = ["'", ";", "--", "/*", "*/", "xp_", "exec", "insert", "delete", "update", "drop", "truncate", "select", "union", "and", "or"]
            # Verifica se a string de entrada contém caracteres da blacklist
            for char in blacklist:
                if char in entrada:
                    g.grava_log(mensagem=f"Database Blacklist: A string {char} foi localizada em {entrada}",tipo="WARNING",modulo=__file__)
                    return True

            # Se não foram encontrados caracteres perigosos, retornamos False
            return False

        if cd_relatorio is None:
            cd_relatorio = ""

        # Verifica se possui algum caracter que pode causar uma falha de segurança
        if blacklist(cd_workspace) or blacklist(cd_relatorio):
            self.status = 400
            self.resultado = "Caracteres inválidos nos parâmetros!"
        else:
            # Cursor para executar consultas
            cursor = self.connection.cursor()

            sql = "SELECT DS_URL, DS_DIRETORIO_RELATIVO, NM_RELATORIO FROM RPACATIVA.POWERBI_RELATORIO WHERE CD_WORKSPACE = '" + cd_workspace +"' AND CD_RELATORIO = NVL('" + cd_relatorio + "',CD_RELATORIO) AND NVL(FL_ATIVO,'F') = 'T'"
            # Executa consultas SQL usando o cursor
            cursor.execute(sql)
            resultado = cursor.fetchall()
            cursor.close()
            

        return resultado
    
    def versao_Sistema(self):
        cursor = self.connection.cursor()

        # Executa consultas SQL usando o cursor
        cursor.execute("SELECT DSVALOR FROM RPACATIVA.TPARAMETROS WHERE DSCAMPO = 'VERSAO_ATUAL_SISTEMA'")

        # Recupere os resultados da consulta
        for linha in cursor:
            coluna = linha
            versao = coluna[0]

        cursor.close()
        return versao
    
    def esta_conectado(self):
        try:
            # Tenta pingar o banco de dados para verificar a conexão
            self.connection.ping()
            retorno = True
        except:
            retorno = False
        return retorno
    
    def consulta_personalizada(self, sql):
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)

            aux = cursor.fetchall()
            cursor.close()

            return aux
        except:
            return None
        
    def consulta_temail(self):
        try:
            cursor = self.connection.cursor()

            sql = """select a.e_from, a.e_to, a.subject,REPLACE(DBMS_LOB.SUBSTR(A.BODY, 4000, 1), '<BR>', ''), a.text_html, a.status, b.documento 
                     from temail a, documento b, temail_anexo c
                     where a.pk_email = c.pk_email
                     and c.pk_documento = b.pk_documento  
                     and a.text_html = 'H'
                     and a.status = 'R'"""
            
            cursor.execute(sql)
            linhas = cursor.fetchall()  # Pega todas as linhas da consulta
            cursor.close()
            return linhas
        except Exception as e:
            print(f'Erro ao consultar o banco de dados: {e}')
            raise
    
    def atualiza_status(self, e_from, e_to, subject):
        try:
            cursor = self.connection.cursor()
            sql = """update temail
                     SET status = 'E'
                     WHERE e_from = :1 AND e_to = :2 AND subject = :3"""
            cursor.execute(sql, (e_from, e_to, subject))
            self.connection.commit()
            cursor.close()
            print(f'Status atualizado para "E" para o e-mail de {e_from} para {e_to} com assunto "{subject}".')
        except Exception as e:
            print(f'Erro ao atualizar o status no banco de dados: {e}')
            raise
