import socket

from waitress import serve
from app import create_app

if __name__ == "__main__":
    """Inicia o serviço Web."""
    app = create_app()
    if 'CTVPOMAP' in socket.getfqdn():
        servidor = socket.getfqdn().split('.')[0].lower()
        serve(app, host=servidor, port=8080)
    else:
        serve(app, host="localhost", port=9443)