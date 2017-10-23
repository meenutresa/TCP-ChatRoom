import socket
import sys
import threading
from threading import Thread

class Server_Thread(Thread):
    def __init__(self,socket):
        Thread.__init__(self)
        self.socket = socket

    def run(self):
        while True:
            msg_to_client = input("Enter the message : ")
            self.socket.send(msg_to_client.encode())
            msg_from_server = self.socket.recv(buff_size).decode()
            if "Bye" in msg_from_server:
                #msg_from_server = self.socket.recv(buff_size).decode()
                #print("<Me> : " + msg_from_server)
                self.socket.close()
                sys.exit()
            else:
                print("<Me> :  " + msg_from_server)


class Server_Broadcast_Thread(Thread):
    def __init__(self,socket):
        Thread.__init__(self)
        self.socket = socket

    def run(self):
        socket2 =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket2.connect((ip, port2))
        while True:
            message = socket2.recv(buff_size).decode()
            print("\n" + message)


buff_size = 2048
ip = sys.argv[1]
port = int(sys.argv[2])
port2 = 125
server_threads = []
socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket1.connect((ip, port))
#COnnected to server
#socket2 =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#socket2.connect((ip, port2))

msg_from_server=socket1.recv(buff_size).decode()
print("Message from Server is : " + msg_from_server)

server_thread = Server_Thread(socket1)
server_thread.daemon = True
server_thread.start()
server_threads.append(server_thread)

server_broadcast_thread = Server_Broadcast_Thread(socket1)
server_broadcast_thread.daemon = True
server_broadcast_thread.start()
server_threads.append(server_broadcast_thread)

while True:
    for st in server_threads:
        st.join(600)
        if not st.isAlive():
            break
    break
