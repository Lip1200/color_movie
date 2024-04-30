import socket
import sys

def start_client(host='127.0.0.1', port=12345, message="Hello!"):
    # Création d'un socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connexion au serveur
    try:
        client_socket.connect((host, port))
        print(f"Connected to server at {host}:{port}")
        
        # Envoyer un message au serveur
        client_socket.sendall(message.encode())
    except Exception as e:
        print(f"Failed to connect to server: {e}")
    finally:
        # Fermer le socket
        client_socket.close()
        print("Connection closed")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 client.py [host] [port]")
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])
        start_client(host, port)
