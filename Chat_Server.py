import socket
import sys
import queue
import threading
from threading import Thread
import re

no_of_clients_connected = 0

class Client_Thread(Thread):
    def __init__(self,socket,ip,port):
        Thread.__init__(self)
        self.socket = socket
        self.ip = ip
        self.port = port
        print ("New Client Thread started")

    def run(self):
        message = "Hello Client"
        self.socket.send(message.encode())
        username = "<" + client_ip + "," + str(client_port) + ">"
        print("from thread no : of threads : " + str(no_of_clients_connected))
        #if no_of_clients_connected == 1:
        msg_from_client=self.socket.recv(buff_size).decode()
        print("Message from Client : " +username+ ":" + msg_from_client)
        msg_split = re.findall(r"[\w']+", msg_from_client)
        chatroom = msg_split[1]
        join_msgto_client = "JOINED_CHATROOM: " + str(chatroom) + "\nSERVER_IP: "+str(ip)+"\nPORT: "+str(port)+"\nROOM_REF: 1"+"\nJOIN_ID: 1"
        self.socket.send(join_msgto_client.encode())
        while True:
            msg_from_client=self.socket.recv(buff_size).decode()
            print("Message from Client : " +username+ ":" + msg_from_client)
            #print("Message from Client : " +username+ ":" + msg_from_client)
            if "Bye" in msg_from_client:
                message = username + "left from chat!!!"
                lock.acquire()
                del send_queues[self.socket.fileno()]
                for i, j in zip(send_queues.values(), send_queues):
                    if j == self.socket.fileno():
                        pass
                    else:
                        i.put(message)
                lock.release()
                msg = "Bye"
                self.socket.send(msg.encode())
                break;
            else:
                message = msg_from_client
                msg = username + " : " + message
                lock.acquire()
                for i, j in zip(send_queues.values(), send_queues):
                    if j == self.socket.fileno():
                        pass
                    else:
                        i.put(msg)
                lock.release()
                self.socket.send(message.encode())
                #print("from thread no : of threads : " + str(no_of_clients_connected))


class Client_Broadcast_Thread(Thread):
    def __init__(self,socket):
        Thread.__init__(self)
        self.socket = socket
        print ("New Client Broadcast Thread started")

    def run(self):
        tcp_socket2.listen(1)
        (client_soc1,addr) = tcp_socket2.accept()
        while True:
            try:
                message = send_queues[self.socket.fileno()].get(False)
                #print("Message in Broadcast class : " + message)
                client_soc1.send(message.encode())
            except queue.Empty:
                message = "No message to broadcast"
            except KeyError as e:
                pass

buff_size = 2048
lock = threading.Lock()
send_queues = {}
ip = '0.0.0.0'
port = int(sys.argv[1])
port2 = 125
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_socket.bind(('',port))

tcp_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_socket2.bind(('', port2))

client_threads = []
while True:
    tcp_socket.listen(6)

    print("Server active. Waiting for Clients to join...")

    (client_soc,(client_ip,client_port)) = tcp_socket.accept()
    # CLient connected
    no_of_clients_connected = no_of_clients_connected + 1
    print("no : of threads : " + str(no_of_clients_connected))
    q = queue.Queue()
    lock.acquire()

    send_queues[client_soc.fileno()] = q
    lock.release()

    print("<" + client_ip + "," + str(client_port) + "> connected")

    client_thread = Client_Thread(client_soc,client_ip,client_port)
    client_thread.daemon = True
    client_thread.start()
    client_threads.append(client_thread)

    client_broadcast_thread = Client_Broadcast_Thread(client_soc)
    client_broadcast_thread.daemon = True
    client_broadcast_thread.start()
    client_threads.append(client_broadcast_thread)

for ct in client_threads:
    ct.join()
    print("Reached the END")
