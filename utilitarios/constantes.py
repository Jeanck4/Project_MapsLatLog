"""
Este módulo é voltado para guardar as constantes utilizadas nesta API.

O objetivo é tornar o código mais legivel e parametrizado.
"""
import os
LINKS = {
    'login': 'https://app.powerbi.com/singleSignOn',
    'dashboard': 'https://app.powerbi.com/groups/1f7131bb-6c34-4ea9-b09a-ddb0d1a98308/reports/a4335ece-7944-41a1-9298-104797969314/ReportSection8e50a5fbc3d827d1ed28?experience=power-bi',
}

PATH = {
    'diretorio_raiz': 'M:\\Cativa\\versao9\\VersaoXXXXXX\\webapps\\uniface',
    'arquivo_cache': os.getcwd() + '\cache',
}

XPATHS = {
    'dashboard': '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]',
}
