import yaml
import socket


def main():
    with open('secrets.yaml', 'r') as file:
        config = yaml.safe_load(file)

    server_host = config['ip']
    server_port = config['port']

    connect_to_server(server_host, server_port)


def connect_to_server(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4 and TCP
    client_socket.connect((host, port))
    print(f"Connected to server {host} on port {port}")

    message = "www.google.com:80".encode()
    client_socket.send(message)

    # Receive the response
    response = b""
    while True:
        data = client_socket.recv(4096)
        if not data:
            break
        response += data
    print(response.decode())

    client_socket.close()


if __name__ == '__main__':
    main()
