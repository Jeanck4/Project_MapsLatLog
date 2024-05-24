"""
Este Módulo tras algumas funções gerais, voltados para depuração do código, e gravação de Logs.
"""

# Importações do Python
import logging
from datetime import datetime
import sys

logging.basicConfig(
   filename=f'C:\\Logs\\log_{datetime.now().strftime("%d%m%Y%H")}.log',  # Nome do arquivo de log
   level=logging.INFO,  # Nível mínimo de mensagens a serem registradas
   format='%(asctime)s - %(levelname)s - %(message)s',  # Formato da mensagem de log
)

class GeneralFuncs:
    """
    Classe responsável por guardar algumas funções internas
    """       
    @staticmethod
    def grava_log(tipo="INFO", mensagem="", modulo=""):
        if GeneralFuncs.is_none_null(mensagem):
            return False
        elif GeneralFuncs.is_none_null(modulo):
            mensagem = f"{mensagem} + [{modulo}]"

        if tipo == "INFO":
            logging.info(mensagem)
            return True
        elif tipo == "DEBUG":
            logging.debug(mensagem)
            return True
        elif tipo == "WARNING":
            logging.warning(mensagem)
            return True
        elif tipo == "ERROR":
            logging.error(mensagem)
            return True
        elif tipo == "CRITICAL":
            logging.critical(mensagem)
            return True
        
        return False
    
    @staticmethod
    def is_none_null(valor):
        if valor is None or valor == '' or valor == "":
            return True
        else:
            return False
        
    def dispara_erro() -> str:
        """ Mostrar mensagem de erro com detalhes """

        exctp, exc, exctb = sys.exc_info()
        print(
            f'\n\033[033mtraceback\033[0m:\033[031m{exc}\033[0m' +
            f'{exctb.tb_frame.f_code.co_name}:{exctb.tb_lineno}:{exctp}:'
        )