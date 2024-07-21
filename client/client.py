import yaml
import socket


def open_connection(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4 and TCP
    client_socket.connect((host, port))
    print(f"Connected to server {host} on port {port}")
    return client_socket


def make_web_request(socket, addr, port):
    message = f"{addr}:{port}"
    try:
        sock.send(message.encode())
    except BrokenPipeError:
        print("Connection reset by server. Cannot send data.")
        sock.close()
        return -1
    except socket.error as e:
        print(f"Failed to send message: {e}")
        raise

    if port == "-1":
        print("Closing Connection...")
        socket.close()
        return -1

    # Receive the response
    # Read the length header
    length_header = b""
    while b"\n" not in length_header:
        length_header += sock.recv(1)
    header_str = length_header.decode('utf-8').strip()  # Remove the newline separator
    if header_str.startswith("length:"):
        data_len = int(header_str.split(":")[1])
    else:
        raise ValueError("Invalid length header received")

    data = b""
    while len(data) < data_len:
        packet = socket.recv(data_len - len(data))
        if not packet:
            print("breaking")
            break
        data += packet

    return data.decode()


if __name__ == '__main__':
    # The VPN's IP and Port are in a secrets file
    # The IP is a standard VPN port so this is a bit overkill
    with open('secrets.yaml', 'r') as file:
        config = yaml.safe_load(file)

    ip = config['ip']
    port = config['port']

    sock = open_connection(ip, port)

    while True:
        dest_addr = input("Web Address: ")
        dest_port = input("Port: ")
        resp = make_web_request(sock, dest_addr, dest_port)
        if resp == -1:
            break
        print("returned")
        print(resp[:16])
