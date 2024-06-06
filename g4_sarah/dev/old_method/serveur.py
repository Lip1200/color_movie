import socket

def start_server(host='127.0.0.1'):
    # création socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # lier du socket à une adresse IP et un port dynamique
    server_socket.bind((host, 0))  # 0 signifie "choisir un port disponible"
    
    # Obtenir le port assigné
    port = server_socket.getsockname()[1]
    
    # Le serveur écoute les connexions entrantes
    server_socket.listen()
    print(f"Server listening on {host}:{port}")
    
    # Accepter une connexion entrante
    client_socket, client_address = server_socket.accept()
    print(f"Connected to {client_address}")
    
    # Recevoir des données du client
    message = client_socket.recv(1024).decode()
    print(f"Received from client: {message}")
    
    # Fermer la connexion
    client_socket.close()
    server_socket.close()
    print("Server closed")

if __name__ == "__main__":
    start_server()
