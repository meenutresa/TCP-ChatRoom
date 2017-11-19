import socket
import sys
import queue
import threading
from threading import Thread
import re
import random

no_of_clients_connected = 0
chatroom_dict = {}
user_dict = {}
user_room = {}
roomcount_user = {}
user_fileno = {}
send_queue_fileno_client = {}

class Client_Thread(Thread):
    def __init__(self,socket,ip,port):
        Thread.__init__(self)
        self.socket = socket
        self.ip = ip
        self.port = port
        self.room_ref = 0
        self.chatroom = ''
        self.client_name = ''
        self.join_id = 0
        print ("New Client Thread started")

    def get_roomID(self):
        for chatrm in chatroom_dict:
            if chatrm == self.chatroom:
                return chatroom_dict[self.chatroom]
        value = len(chatroom_dict)+1
        chatroom_dict[self.chatroom.lower()]=value
        return value

    def get_clientID(self):
        for id in user_dict:
            if id == self.client_name:
                return user_dict[self.client_name]
        return self.set_clientID()

    def set_clientID(self):
        value = len(user_dict)+1
        user_dict[self.client_name]=value
        return value

    def set_user_room(self):
        for room in user_room:
            if self.room_ref == room:
                user_room[self.room_ref].append(self.join_id)
                return
        user_room[self.room_ref] = [self.join_id]

    def set_roomcount_user(self):
        for user in roomcount_user:
            if user == self.join_id:
                roomcount_user[self.join_id] = roomcount_user[self.join_id]+1
                return
        roomcount_user[self.join_id] = 1

    def reduce_roomcount_user(self):
        roomcount_user[self.join_id] = roomcount_user[self.join_id]-1
        if roomcount_user[self.join_id] == 0:
            del roomcount_user[self.join_id]

    def remove_user_from_room(self):
        user_room[self.room_ref].remove(self.join_id)

    def get_users_in_room(self):
        #print("get_users_in_room : ",self.room_ref)
        return user_room[self.room_ref]

    def get_users_in_room_chat_conv(self,conv_roomref):
        #print("get_users_in_room : ",self.room_ref)
        return user_room[conv_roomref]

    def set_user_fileno(self):
        user_fileno[(self.room_ref,self.join_id)] = self.socket.fileno()

    def get_user_fileno(self, other_join_id):
        return user_fileno[(self.room_ref,other_join_id)]

    def delete_user_fileno(self):
        del user_fileno[(self.room_ref,self.join_id)]

    def broadcast(self,file_no):
        try:
            message = send_queues[file_no].get(False)
            print("Message in Broadcast class : " + message)
            print("Broadcast socket: ",send_queue_fileno_client[file_no])
            send_queue_fileno_client[file_no].send(message.encode())
        except queue.Empty:
            message = "No message to broadcast"
        except KeyError as e:
            pass

    def broadcast_data(self):
        send_queue_fileno_client[self.socket.fileno()] = self.socket


    def run(self):
        #message = "Hello Client"
        #self.socket.send(message.encode())
        username = "<" + client_ip + "," + str(client_port) + ">"
        print("from thread no : of threads : " + str(no_of_clients_connected))
        #if no_of_clients_connected == 1:
        #------------------------------------------------------
        #msg_from_client=self.socket.recv(buff_size).decode()
        #print("Message from Client : " +username+ ":" + msg_from_client)
        #--------------------------------------------------

        while True:
            msg_from_client=self.socket.recv(buff_size).decode()
            #print("Message from Client : " +self.client_name+ ":" + msg_from_client)
            #print("Message from Client : " +username+ ":" + msg_from_client)
            if "JOIN_CHATROOM" in msg_from_client:
                msg_split = re.findall(r"[\w']+", msg_from_client)
                self.chatroom = msg_split[1]
                self.client_name = msg_split[7]
                self.room_ref = self.get_roomID()
                self.join_id = self.get_clientID()
                self.set_user_room()
                self.set_roomcount_user()
                self.set_user_fileno()
                self.broadcast_data()
                #print("user_fileno : ", user_fileno)
                join_msgto_client = "JOINED_CHATROOM: " + str(self.chatroom) + "\nSERVER_IP: "+str(ip)+"\nPORT: "+str(port)+"\nROOM_REF: "+str(self.room_ref)+"\nJOIN_ID: "+str(self.join_id)+"\n"
                self.socket.send(join_msgto_client.encode())
                allusers_in_room = self.get_users_in_room()
                #print("\nall users in room :",allusers_in_room)
                join_message_to_room = str(self.client_name) + " has joined this chatroom\n"
                join_message_to_room_format = "CHAT: "+ str(self.room_ref) + "\nCLIENT_NAME: "+str(self.client_name) + "\nMESSAGE: "+str(join_message_to_room)+"\n"
                lock.acquire()
                #print("\nsend_queues :" , send_queues)
                #del send_queues[self.socket.fileno()]
                Tosend_fileno = []
                for user_id in allusers_in_room:
                    Tosend_fileno.append(self.get_user_fileno(user_id))
                for i, j in zip(send_queues.values(), send_queues):
                    if j in Tosend_fileno:
                        i.put(join_message_to_room_format)
                        #self.broadcast(j)
                lock.release()
                for ts in Tosend_fileno:
                    self.broadcast(ts)
            elif "HELO" in msg_from_client:
                host_name = socket.gethostname()
                host_ip = socket.gethostbyname(host_name)
                host_port = port
                message = str(msg_from_client)+"\nIP:"+str(host_ip)+"\nPort:"+str(host_port)+"\nStudentID:17312351\n"
                self.socket.send(message.encode())
            elif "KILL_SERVICE" in msg_from_client:
                pass
            elif "LEAVE_CHATROOM" in msg_from_client:
                message = self.client_name + " has left this chatroom!!!"
                leave_message_format = "CHAT: "+ str(self.room_ref) + "\nCLIENT_NAME: "+str(self.client_name) + "\nMESSAGE: "+str(message)+"\n"
                allusers_in_room = self.get_users_in_room()
                lock.acquire()
                #del send_queues[self.socket.fileno()]
                Tosend_fileno = []
                for user_id in allusers_in_room:
                    #print("userid : ",user_id)
                    Tosend_fileno.append(self.get_user_fileno(user_id))
                for i, j in zip(send_queues.values(), send_queues):
                    if j in Tosend_fileno and j != self.socket.fileno():
                        i.put(leave_message_format)
                lock.release()
                for ts in Tosend_fileno:
                    self.broadcast(ts)

                self.remove_user_from_room()
                self.reduce_roomcount_user()
                self.delete_user_fileno()
                msg = "LEFT_CHATROOM: " + str(self.room_ref) + "\nJOIN_ID: " + str(self.join_id)+"\n"
                self.socket.send(msg.encode())
                break;
            else:
                message = msg_from_client
                print("Message : ", message)
                msg_split = re.findall(r"[\w']+", msg_from_client)
                print("Split message :", msg_split)
                conv_client_name = msg_split[5]
                conv_room_ref = msg_split[1]
                conv_join_id = msg_split[3]
                msg = "CHAT: " + str(conv_room_ref) + "\nCLIENT_NAME: " + str(conv_client_name) + "\nMESSAGE: " + str(message) + "\n"
                #print("Room_Ref : ", self.room_ref)
                #for rr in user_room:
                #    print(rr)
                allusers_in_room = self.get_users_in_room_chat_conv(conv_room_ref)
                #print("user_fileno : ", user_fileno)
                lock.acquire()
                Tosend_fileno = []
                for user_id in allusers_in_room:
                    #print("userid : ",user_id)
                    Tosend_fileno.append(self.get_user_fileno(user_id))
                for i, j in zip(send_queues.values(), send_queues):
                    if j in Tosend_fileno and j != self.socket.fileno():
                        i.put(msg)
                lock.release()
                for ts in Tosend_fileno:
                    self.broadcast(ts)
                self.socket.send(msg.encode())
                #print("from thread no : of threads : " + str(no_of_clients_connected))


"""
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
"""


buff_size = 2048
lock = threading.Lock()
send_queues = {}
ip = '0.0.0.0'
port = int(sys.argv[1])
port2 = 5000
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_socket.bind(('',port))

#tcp_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#tcp_socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#tcp_socket2.bind(('', port2))

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
    #broadcast_data(client_soc,q)
    lock.release()

    print("<" + client_ip + "," + str(client_port) + "> connected")

    client_thread = Client_Thread(client_soc,client_ip,client_port)
    client_thread.daemon = True
    client_thread.start()
    client_threads.append(client_thread)
""""
    client_broadcast_thread = Client_Broadcast_Thread(client_soc)
    client_broadcast_thread.daemon = True
    client_broadcast_thread.start()
    client_threads.append(client_broadcast_thread)
    """

for ct in client_threads:
    ct.join()
    print("Reached the END")
