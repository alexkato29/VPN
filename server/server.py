import socket
import threading


def start_server(port):
    # Create a socket object using IPv4 and TCP protocol
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to all available IP addresses on the specified port
    server_socket.bind(('', port))

    # Enable the server to accept connections (max 5 clients in the waiting queue)
    server_socket.listen(5)
    print(f"Server is listening on port {port}...")
    return server_socket


def handle_client(client_socket):
    while True:
        # Receive the IP and Port from the client
        data = client_socket.recv(1024)  # buffer size is 1024 bytes
        if len(data) == 0:
            continue

        vals = data.decode().split(':')

        if len(vals) != 2:
            remote_address = client_socket.getpeername()
            print(f"Resetting connection to {remote_address}")
            client_socket.shutdown(socket.SHUT_RDWR)  # This will send an RST packet
            client_socket.close()
            continue

        ip = vals[0]
        port = vals[1]
        port = int(port)

        if port == -1:
            remote_address = client_socket.getpeername()
            client_socket.close()
            print(f"Closing connection to {remote_address}")
            break

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

        # Sending a length header to the client to let them know to stop waiting
        client_socket.send(f"length:{len(response)}\n".encode())

        # Forward it to the client
        total_sent = 0
        while total_sent < len(response):
            sent = client_socket.send(response[total_sent:])
            if sent == 0:
                raise RuntimeError("Socket connection broken")
            total_sent += sent


def accept_connections(server_socket):
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connected to {addr}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()


if __name__ == '__main__':
    server_socket = start_server(1194)
    accept_thread = threading.Thread(target=accept_connections, args=(server_socket,))
    accept_thread.start()
