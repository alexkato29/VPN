import socket


def start_server(port):
    # Create a socket object using IPv4 and TCP protocol
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to all available IP addresses on the specified port
    server_socket.bind(('', port))

    # Enable the server to accept connections (max 1 clients in the waiting queue)
    server_socket.listen(5)
    print(f"Server is listening on port {port}...")

    while True:
        # Accept a connection from a client
        client_socket, addr = server_socket.accept()
        print(f"Connected to {addr}")

        # Receive the IP and Port from the client
        data = client_socket.recv(1024)  # buffer size is 1024 bytes
        ip, port = data.decode().split(':')
        port = int(port)

        print(f"Received Address: {ip}:{port}")

        # Connect to the server
        proxied_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxied_socket.connect((ip, port))

        # Build the HTTP request
        request = f"GET / HTTP/1.1\r\nHost: {ip}\r\nConnection: close\r\n\r\n"
        request = request.encode()
        proxied_socket.sendall(request)

        # Receive the response
        response = b""
        while True:
            data = proxied_socket.recv(4096)
            if not data:
                break
            response += data

        # Forward it to the client
        client_socket.sendall(response)

        # Close the connection with the client
        client_socket.close()


if __name__ == '__main__':
    start_server(1194)
