import socket
import sys

buff_size = 2048
ip = sys.argv[1]
port = int(sys.argv[2])
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((ip, port))
#COnnected to server
msg_from_server=socket.recv(buff_size).decode()

print("Message from Server is : " + msg_from_server)

while True:
    msg_to_client = input("Enter the message : ")
    socket.send(msg_to_client.encode())
    msg_from_server = socket.recv(buff_size).decode()
    print("Message from server : " + msg_from_server)
    if "Bye" in msg_from_server:
        msg_from_server = socket.recv(buff_size).decode()
        print("Message from server : " + msg_from_server)
        socket.close()
        sys.exit()
