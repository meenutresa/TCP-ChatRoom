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
room_user = {}
user_fileno = {}
send_queue_fileno_client = {}

class Client_Thread(Thread):
    def __init__(self,socket,ip,port):
        Thread.__init__(self)
        self.socket = socket
        self.ip = ip
        self.port = port
        #self.room_ref = 0
        #self.chatroom = ''
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
    def get_roomID_join(self,chat_chatroom):
        for chatrm in chatroom_dict:
            if chatrm == chat_chatroom:
                return chatroom_dict[chat_chatroom]
        value = len(chatroom_dict)+1
        chatroom_dict[chat_chatroom.lower()]=value
        return value

    def get_clientID(self):
        for id in user_dict:
            if id == self.client_name:
                return user_dict[self.client_name]
        return self.set_clientID()

    def get_clientID_disco(self,disc_clientname):
        return user_dict[disc_clientname]

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
    def set_user_room_chat(self,chat_roomref):
        for room in user_room:
            if chat_roomref == room:
                user_room[chat_roomref].append(self.join_id)
                return
        user_room[chat_roomref] = [self.join_id]

    def set_roomcount_user(self):
        for user in roomcount_user:
            if user == self.join_id:
                roomcount_user[self.join_id] = roomcount_user[self.join_id]+1
                return
        roomcount_user[self.join_id] = 1

    def set_room_user(self,join_roomref):
        for user in room_user:
            if user == self.client_name:
                for room in room_user[self.client_name]:
                    if room == join_roomref:
                        return
                room_user[self.client_name].append(join_roomref)
                return
        room_user[self.client_name] = [join_roomref]

    def remove_room_user_dico(self,disc_roomref):
        room_user[self.client_name].remove(disc_roomref)

    def get_room_user_disco(self):
        l=[]
        try:
            return room_user[self.client_name]
        except KeyError as e:
            return l

    def reduce_roomcount_user(self):
        roomcount_user[self.join_id] = roomcount_user[self.join_id]-1
        if roomcount_user[self.join_id] == 0:
            del roomcount_user[self.join_id]

    def reduce_roomcount_user_disco(self,disc_joinid):
        #print("disc_joinid",disc_joinid)
        #print("roomcount_user",roomcount_user)
        try:
            roomcount_user[disc_joinid] = roomcount_user[disc_joinid]-1
            if roomcount_user[disc_joinid] == 0:
                del roomcount_user[disc_joinid]
        except:
            pass

    def remove_user_from_room(self):
        user_room[self.room_ref].remove(self.join_id)
    def remove_user_from_room_leave(self,leave_roomref):
        user_room[leave_roomref].remove(self.join_id)

    def remove_user_from_room_leave_disco(self,disc_roomref,disc_joinid):
        #print("disc_roomref",disc_roomref)
        #print("disc_joinid",disc_joinid)
        #print("user_room",user_room)
        for jid in user_room[disc_roomref]:
            if jid == disc_joinid:
                user_room[disc_roomref].remove(disc_joinid)

    def get_users_in_room(self):
        #print("get_users_in_room : ",self.room_ref)
        return user_room[self.room_ref]

    def get_users_in_room_chat_conv(self,conv_roomref):
        #print("get_users_in_room : ",self.room_ref)
        return user_room[conv_roomref]

    def set_user_fileno(self):
        user_fileno[(self.room_ref,self.join_id)] = self.socket.fileno()
    def set_user_fileno_chat(self,chat_roomref):
        user_fileno[(chat_roomref,self.join_id)] = self.socket.fileno()

    def get_user_fileno(self, other_join_id):
        return user_fileno[(self.room_ref,other_join_id)]
    def get_user_fileno_gen(self, gen_roomref, other_join_id):
        return user_fileno[(gen_roomref,other_join_id)]

    def delete_user_fileno(self):
        del user_fileno[(self.room_ref,self.join_id)]
    def delete_user_fileno_leave(self,leave_roomref):
        del user_fileno[(leave_roomref,self.join_id)]

    def delete_user_fileno_leave_disco(self,disc_roomref,disc_joinid):
        try:
            del user_fileno[(disc_roomref,disc_joinid)]
        except KeyError as e:
            pass

    def broadcast(self,file_no):
        try:
            message = send_queues[file_no].get(False)
            print("Message in Broadcast class : " + message)
            #print("Broadcast socket: ",send_queue_fileno_client[file_no])
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
        flag=1
        client4 = 'n'
        #if no_of_clients_connected == 1:
        #------------------------------------------------------
        #msg_from_client=self.socket.recv(buff_size).decode()
        #print("Message from Client : " +username+ ":" + msg_from_client)
        #--------------------------------------------------
        while True:
            msg_from_client=self.socket.recv(buff_size).decode()
            #if flag!=1:
            #    print("Client_Threads",client_threads)
            #    print("Client_Threads",self.client_nam)
            #    sys.exit()
            #print("Message from Client : " +self.client_name+ ":" + msg_from_client)
            #print("Message from Client : " +username+ ":" + msg_from_client)
            if "HELO" in msg_from_client:
                print("Message : ", msg_from_client)
                conv_message_1 = msg_from_client.split(':')
                print("conv_message_1",conv_message_1)
                msg_split = re.findall(r"[\w']+", msg_from_client)
                message = msg_split[1]
                host_name = socket.gethostname()
                host_ip = socket.gethostbyname(host_name)
                host_port = port
                message = str(conv_message_1[0])+"IP:"+str(host_ip)+"\nPort:"+str(host_port)+"\nStudentID:17312351\n"
                self.socket.send(message.encode())
            elif "KILL_SERVICE" in msg_from_client:
                #flag =0
                print("Message in KILL_SERVICE : ", msg_from_client)
                #tcp_socket.close()
                #break;
                #tcp_socket.close(
                #break;
            elif "DISCONNECT" in msg_from_client:
                if client4 != 'y':
                    print("Message : ", msg_from_client)
                    #conv_message_1 = msg_from_client.split(':')
                    #print("conv_message_1",conv_message_1)
                    msg_split = re.findall(r"[\w']+", msg_from_client)
                    disconnect_client_name = msg_split[5]
                    #if disconnect_client_name == 'client'
                    print("self.client name",self.client_name)
                    print("disconnect_client_name",disconnect_client_name)

                    diconnect_joinid = self.get_clientID_disco(disconnect_client_name)
                    roomlist_of_disc_client = self.get_room_user_disco()
                    message = disconnect_client_name + " has left this chatroom"
                    #print("roomlist_of_disc_client",roomlist_of_disc_client)
                    #self.socket.send(msg.encode())
                    flag=0
                    #client4 = 'n'
                    if disconnect_client_name=="client4":
                        client4 = 'y'
                    for dr in roomlist_of_disc_client:
                        flag=1
                        print("chatroom_dict",chatroom_dict)
                        print("user_dict",user_dict)
                        print("user_room",user_room)
                        print("roomcount_user",roomcount_user)
                        print("room_user",room_user)
                        print("user_fileno",user_fileno)
                        print("rooms_refs : ",dr)
                        disconnect_message_format = "CHAT: "+str(dr)+ "\nCLIENT_NAME: "+str(disconnect_client_name) + "\nMESSAGE: "+str(message)+"\n\n"
                        allusers_in_room = self.get_users_in_room_chat_conv(dr)
                        print("allusers_in_room",allusers_in_room)
                        #self.socket.send(disconnect_message_format.encode())
                        lock.acquire()
                        #del send_queues[self.socket.fileno()]
                        Tosend_fileno = []
                        for user_id in allusers_in_room:
                            #print("userid : ",user_id)
                            Tosend_fileno.append(self.get_user_fileno_gen(dr,user_id))
                        for i, j in zip(send_queues.values(), send_queues):
                            if j in Tosend_fileno:
                                print("Tosend_fileno",Tosend_fileno)
                                print("send_queue_fileno_client",send_queue_fileno_client)
                                i.put(disconnect_message_format)
                        lock.release()
                        for ts in Tosend_fileno:
                            self.broadcast(ts)
                        #self.remove_user_from_room_leave_disco(dr,diconnect_joinid)
                        #print("roomlist_of_disc_client before delete",roomlist_of_disc_client)
                        #self.remove_room_user_dico(dr)
                        #print("roomlist_of_disc_client_after delete",roomlist_of_disc_client)
                        self.remove_user_from_room_leave(dr)
                        self.delete_user_fileno_leave(dr)
                        #self.remove_room_user_dico(dr)
                        self.reduce_roomcount_user()
                        #print(user_room)
                        #print("Break")
                    #self.socket.send(disconnect_message_format.encode())
                    if flag !=0:
                        room_user.pop(self.client_name, None)
                    if flag!=1:
                        msg = "ERROR_CODE: "+str(1)+"\nERROR_DESCRIPTION: error occured"
                        #self.socket.send(msg.encode())

                    print("room_user",room_user)
            elif "JOIN_CHATROOM" in msg_from_client:
                print("Message : ", msg_from_client)
                msg_split = re.findall(r"[\w']+", msg_from_client)
                join_chatroom = msg_split[1]
                self.client_name = msg_split[7]
                join_room_ref = self.get_roomID_join(join_chatroom)
                self.join_id = self.get_clientID()
                self.set_user_room_chat(join_room_ref)
                self.set_roomcount_user()
                self.set_room_user(join_room_ref)
                self.set_user_fileno_chat(join_room_ref)
                self.broadcast_data()
                #print("user_fileno : ", user_fileno)
                join_msgto_client = "JOINED_CHATROOM: " + str(join_chatroom) + "\nSERVER_IP: "+str(ip)+"\nPORT: "+str(port)+"\nROOM_REF: "+str(join_room_ref)+"\nJOIN_ID: "+str(self.join_id)+"\n"
                self.socket.send(join_msgto_client.encode())
                allusers_in_room = self.get_users_in_room_chat_conv(join_room_ref)
                #print("\nall users in room :",allusers_in_room)
                join_message_to_room = str(self.client_name) + " has joined this chatroom"
                join_message_to_room_format = "CHAT: "+ str(join_room_ref) + "\nCLIENT_NAME: "+str(self.client_name) + "\nMESSAGE: "+str(join_message_to_room)+"\n\n"
                lock.acquire()
                #print("\nsend_queues :" , send_queues)
                #del send_queues[self.socket.fileno()]
                Tosend_fileno = []
                for user_id in allusers_in_room:
                    Tosend_fileno.append(self.get_user_fileno_gen(join_room_ref,user_id))
                for i, j in zip(send_queues.values(), send_queues):
                    if j in Tosend_fileno:
                        i.put(join_message_to_room_format)
                        #self.broadcast(j)
                lock.release()
                for ts in Tosend_fileno:
                    self.broadcast(ts)
            elif "LEAVE_CHATROOM" in msg_from_client:
                print("Message : ", msg_from_client)
                msg_split = re.findall(r"[\w']+", msg_from_client)
                print("Split message :", msg_split)
                leave_client_name = msg_split[5]
                leave_room_ref = int(msg_split[1])
                leave_join_id = msg_split[3]

                msg = "LEFT_CHATROOM: " + str(leave_room_ref) + "\nJOIN_ID: " + str(leave_join_id)+"\n"
                self.socket.send(msg.encode())
                message = leave_client_name + " has left this chatroom"
                leave_message_format = "CHAT: "+ str(leave_room_ref) + "\nCLIENT_NAME: "+str(leave_client_name) + "\nMESSAGE: "+str(message)+"\n\n"
                if len(send_queues.values())>1:
                    allusers_in_room = self.get_users_in_room_chat_conv(leave_room_ref)
                    lock.acquire()
                    #del send_queues[self.socket.fileno()]
                    Tosend_fileno = []
                    for user_id in allusers_in_room:
                        #print("userid : ",user_id)
                        Tosend_fileno.append(self.get_user_fileno_gen(leave_room_ref,user_id))
                    for i, j in zip(send_queues.values(), send_queues):
                        if j in Tosend_fileno:
                            i.put(leave_message_format)
                    lock.release()
                    for ts in Tosend_fileno:
                        self.broadcast(ts)
                    self.remove_user_from_room_leave(leave_room_ref)
                    self.remove_room_user_dico(leave_room_ref)
                    self.reduce_roomcount_user()
                    self.delete_user_fileno_leave(leave_room_ref)
                    print(user_room)
                    print("Break")
                else:
                    self.remove_user_from_room_leave(leave_room_ref)
                    self.remove_room_user_dico(leave_room_ref)
                    self.reduce_roomcount_user()
                    self.delete_user_fileno_leave(leave_room_ref)

            else:
                if len(msg_from_client)>0:
                    if "CHAT:" in msg_from_client:
                        print("Message : ", msg_from_client)
                        message = msg_from_client
                        print("Message : ", message)
                        msg_split = re.findall(r"[\w']+", msg_from_client)
                        print("Split message :", msg_split)
                        conv_client_name = msg_split[5]
                        conv_room_ref = int(msg_split[1])
                        conv_join_id = msg_split[3]
                        msgsplit = message.split(':')
                        conv_message = msgsplit[len(msgsplit)-1]
                        #conv_message = msg_split[7]
                        #for msgsp in msg_split[8:]:
                        #    conv_message = conv_message +" "+ msgsp
                        msg = "CHAT: " + str(conv_room_ref) + "\nCLIENT_NAME: " + str(conv_client_name) + "\nMESSAGE: " + str(conv_message)
                        print("msg chat : ",msg)
                        #print("Room_Ref : ", self.room_ref)
                        #for rr in user_room:
                        #    print(rr)
                        if len(send_queues.values())>1:
                            allusers_in_room = self.get_users_in_room_chat_conv(conv_room_ref)
                            #print("user_fileno : ", user_fileno)
                            lock.acquire()
                            Tosend_fileno = []
                            for user_id in allusers_in_room:
                                #print("userid : ",user_id)
                                Tosend_fileno.append(self.get_user_fileno_gen(conv_room_ref,user_id))
                            for i, j in zip(send_queues.values(), send_queues):
                                if j in Tosend_fileno:
                                    i.put(msg)
                            lock.release()
                            for ts in Tosend_fileno:
                                self.broadcast(ts)
                        else:
                            self.socket.send(msg.encode())
                        #self.socket.send(msg.encode())
                        #print("from thread no : of threads : " + str(no_of_clients_connected))
                    else:
                        msg = "CHAT: "+str(0)+"\nCLIENT_NAME: "+self.client_name+"\n"+self.client_name+" has left this chatroom."
                        print("msg chat : ",msg)
                        self.socket.send(msg.encode())

        print("Out of while loop")
        #sys.exit()
        #sys.exit()


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
tcp_socket.listen(5)

#tcp_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#tcp_socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#tcp_socket2.bind(('', port2))

client_threads = []
while True:

    print("Server active. Waiting for Clients to join...")
    try:
        (client_soc,(client_ip,client_port)) = tcp_socket.accept()
    except OSError as err:
        pass
        #sys.exit()
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
"""
for ct in client_threads:
    ct.join()
    print("Reached the END
"""
