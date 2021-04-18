import socket
import threading
import json
import time

try:
    SERVER = socket.gethostbyname(
        socket.gethostname())  # gethostbyname - It returns the host ip address by the host name i.e the computer name
    # in my case my pc name is 'LAPTOP-0S4230UG' so by 'gethostname' we can get host name
    PORT = 5050
    FORMAT = 'utf-8'
    BUFFER = 64

    clients = {}  # dictionary  of names of clients associated with their socket object.
    # socket.socket() creates a socket object
    server = socket.socket(socket.AF_INET,
                           socket.SOCK_STREAM)  # AF_INET is the Internet address family for IPv4. SOCK_STREAM is the socket type
    # for TCP, the protocol that will be used to transport our messages in the network

    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((SERVER,
                 PORT))  # bind() method which binds it to a specific ip and port so that it can listen to incoming requests on that ip and port


    def client_txt(d):
        with open('client_data.json', 'w') as file:
            k = list(d.keys())
            json.dump(k, file)
            file.close()


    def send_client(name):
        return clients[name]


    def handle_client(client, username):
        try:
            print(f"Hola! [NEW USER CONNECTED] {username} connected.")
            welcome = bytes("Welcome to the DogEyes server!", FORMAT)
            welcome += b' ' * (64 - len(welcome))
            client.send(
                welcome)  # socket.send(bytes) this method takes bytes as argument. We are sending msg to the client beacuse we can ensure that connection has
            # been established. 'bytes' method will convert the string to utf-8 byte format.

            connected = True
            while connected:
                msg_length = client.recv(BUFFER).decode(FORMAT)
                if msg_length:
                    msg_length = int(msg_length)
                    msg_recv = client.recv(msg_length).decode(FORMAT)
                    if msg_recv =="":
                        continue

                    if msg_recv == "DISCONNECT":
                        print(f"{username} is going to disconnect")
                        time.sleep(1.5)
                        clients.pop(username)
                        client_txt(clients)
                        break

                    if msg_recv == "ACTIVE":  # Check the active threads.
                        active_users()
                        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}\n")

                    if "BROADCAST" in msg_recv:
                        broadCast(msg_recv[10:])

                    if "CONNECT" in msg_recv:  # Peer2peer connection
                        c_connect = msg_recv.split()
                        soc_obj = send_client(c_connect[1])
                        soc_obj.send((f"INCOMING CONNECTION {username}").encode('utf-8'))
                        while True:
                            clientMsg_length = client.recv(BUFFER).decode(FORMAT)
                            if clientMsg_length:
                                clientMsg_length = int(clientMsg_length)

                                clientMsg_recv = client.recv(clientMsg_length).decode(FORMAT)
                                if clientMsg_recv == "LEAVE":  # Leave Peer2Peer
                                    leave_alert = (f"DISCONNECTING {username}").encode('utf-8')
                                    len_msg = str(len(leave_alert)).encode('utf-8')
                                    soc_obj.send(len_msg)
                                    soc_obj.send(leave_alert)
                                    break
                                msg_encode = clientMsg_recv.encode('utf-8')  # Client msg encode
                                msg_length = len(
                                    msg_encode)  # msg_length is used to send the length of the message to the server.
                                send_length = str(msg_length).encode('utf-8')
                                send_length += b' ' * (BUFFER - len(send_length))
                                soc_obj.send(send_length)
                                soc_obj.send(msg_encode)

                    print(f"[{username}] >> {msg_recv}")
                    # client.send("Message Recieved.".encode(FORMAT))
            client.close()  # sending message to the client and receiving all the messages from the server the client connection gets closed.
            # sys.exit()
        except:
            clients.pop(username)
            client_txt(clients)


    def active_users():
        print("Active users =>")
        for user in clients.keys():
            print(user)


    def start():
        server.listen(
            5)  # listen() method which puts the server into listen mode. This allows the server to listen to incoming connections
        # listen(5) means that if we have many incoming connects then listen(5) will make those incoming connects into a queue of 5 incoming connection.
        # so when the present connects gets free then new connection is sent from the queue to the socket.

        print(f"[LISTENING] Server is listening on {SERVER}\n")

        while True:
            clientsocket, addr = server.accept()  # This method initiates a connection with the client. 'clientsocket' is client socket object , 'addr' is client ip and port addresses

            # clientsocket.send("NAME:?".encode(FORMAT))

            while True:
                username = clientsocket.recv(64).decode(FORMAT)

                if username in clients.keys():
                    clientsocket.send("The username already exits, please try again.".encode(FORMAT))
                else:
                    clientsocket.send("Username created successfully".encode(FORMAT))
                    clients[username] = clientsocket
                    break

            active_users()  # Display actve users.
            client_txt(clients)  # save client socket object dictionary with usernames

            thread = threading.Thread(target=handle_client,
                                      args=(clientsocket, username))  # Threading for handling multiple clients
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}\n")  # Number of active threads.


    def broadCast(message):
        mes = message.encode('utf-8')
        broad = (f"BROADCAST {len(mes)}").encode('utf-8')

        broad += b' ' * (BUFFER - len(broad))


        for client in clients.values():
            client.send(broad)
            client.send(mes)


    def user_connect(socket):
        pass


    print("""THESE ARE THE SPECIAL COMMANDS TO USE DOGEYES SERVER.
    1.ACTIVE- This shows number of active users
    2.DISCONNECT - This is used for disconnecting the server.
    3.CONNECT - This is used to connect the active clients.
    4.BROADCAST {message}- This is used to broadcast message to all clients in the server.""")
    start()


except socket.error as err:
    print("socket creation failed with error %s" % (err))
