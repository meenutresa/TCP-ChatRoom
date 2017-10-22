import socket
import sys

buff_size = 2048
ip = '0.0.0.0'
port = int(sys.argv[1])
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_socket.bind(('',port))

tcp_socket.listen(1)

print("Server active. Waiting for Clients to join...")

(client_soc,(client_ip,client_port)) = tcp_socket.accept()
# CLient connected
print("<" + client_ip + "," + str(client_port) + "> connected")

message = "Hello Client"
client_soc.send(message.encode())

while True:
    msg_from_client=client_soc.recv(buff_size).decode()
    message = msg_from_client
    client_soc.send(message.encode())
    if "Bye" in msg_from_client:
        message = "Thank You for Joining!!!"
        client_soc.send(message.encode())
        tcp_socket.close()
        sys.exit()
