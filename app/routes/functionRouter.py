# importações do Python
import subprocess
import os
import winreg

# Importações de Bibliotecas Externas
from flask import Blueprint, jsonify, make_response

function_bp = Blueprint('function', __name__)

@function_bp.route("/logoffrdp", methods=['POST'])
def index():
    usuario_sessao = os.getenv('USERNAME')
    powershell_script = f'''
    $session = (query user {usuario_sessao} | Select-Object -Skip 1 | ForEach-Object {{ $_.Trim() -split '\s+' }} | Select-Object -Index 2)
    tscon.exe $session /dest:console'''

    # Arquivo temporário para armazenar o script PowerShell
    path_script = os.path.join(os.environ['TEMP'], 'exec_script.ps1')
    with open(path_script, 'w') as arquivo_script:
        arquivo_script.write(powershell_script)

    # Comando PowerShell para executar o script
    comando = f'powershell -ExecutionPolicy Bypass -File "{path_script}"'

    try:
        # Executa o comando PowerShell
        subprocess.run(comando, check=True, shell=True)
        return make_response(jsonify({"resultado": "Sessão RDP encerrada!"}))
    except subprocess.CalledProcessError as e:
        return make_response(jsonify({"resultado": "Erro ao encerrar sessão RDP!"}))
    finally:
        # Remove o arquivo temporário do script PowerShell
        os.remove(path_script)

@function_bp.route("/cleanup/<opcao>", methods=['POST'])
def cachecleanup(opcao):
    if opcao:
        match opcao:
            case 'system':
                verificar_e_alterar_registro()
                #subprocess.run("cleanmgr /sagerun:6969", shell=True)
            case 'browser':
                ...
    # Executa a limpeza de disco do SO
    # subprocess.run("cleanmgr /sagerun:1", shell=True)
                
def verificar_e_alterar_registro():
    return None # Será desenvolvido para a próxima versão...
    registros = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Active Setup Temp Folders",
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Downloaded Program Files",
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Internet Cache Files",
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Temporary Files",
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Update Cleanup",
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Windows Defender"
    ]
    for reg_path in registros:
        try:
            # Abra a chave do Registro
            chave = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ)
            
            # Tente ler o valor do registro StateFlags6969
            try:
                valor, _ = winreg.QueryValueEx(chave, "StateFlags6969")
                if valor == 2:
                    print(f"O registro StateFlags6969 em {reg_path} já está flegado com valor 2.")
                else:
                    # Altere o valor para 2
                    winreg.SetValueEx(chave, "StateFlags6969", 0, winreg.REG_DWORD, 2)
                    print(f"O registro StateFlags6969 em {reg_path} foi flegado com valor 2.")
            except FileNotFoundError:
                # Se o valor não existir, crie-o e defina o valor como 2
                winreg.SetValueEx(chave, "StateFlags6969", 0, winreg.REG_DWORD, 2)
                print(f"O registro StateFlags6969 em {reg_path} foi criado e flegado com valor 2.")
            
            # Feche a chave do Registro
            winreg.CloseKey(chave)
        except OSError as e:
            print(f"Erro ao acessar o Registro: {e}\n {chave}")