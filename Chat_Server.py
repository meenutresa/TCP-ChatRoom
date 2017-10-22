import socket
import sys
import queue
import threading
from threading import Thread
from socketserver import ThreadingMixIn

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
        while True:
            msg_from_client=self.socket.recv(buff_size).decode()
            message = msg_from_client
            self.socket.send(message.encode())
            print("from thread no : of threads : " + str(no_of_clients_connected))
            if "Bye" in msg_from_client:
                message = "Thank You for Joining!!!"
                self.socket.send(message.encode())
                break;



buff_size = 2048
lock = threading.Lock()
send_queues = {}
ip = '0.0.0.0'
port = int(sys.argv[1])
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_socket.bind(('',port))
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

    '''
    message = "Hello Client"
    client_soc.send(message.encode())

    msg_from_client=client_soc.recv(buff_size).decode()
    message = msg_from_client
    client_soc.send(message.encode())
    if "Bye" in msg_from_client:
        message = "Thank You for Joining!!!"
        client_soc.send(message.encode())
        tcp_socket.close()
        sys.exit()
        '''
for ct in client_threads:
    ct.join()
    print("Reached the END")
