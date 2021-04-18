import socket
import json
import threading
import time


global name
global flag
global c_user
global clients

try:
    SERVER = socket.gethostbyname(
        socket.gethostname())  # gethostbyname - It returns the host ip address by the host name i.e the computer name
    # in my case my pc name is 'LAPTOP-0S4230UG' so by 'gethostname' we can get host name
    PORT = 5050
    FORMAT = 'utf-8'
    BUFFER = 64
    DISCONNECTED = "DISCONNECT"
    msg_str = ""  # In this the msg string gets added until the message ends.
    # socket.socket() creates a socket object
    server = socket.socket(socket.AF_INET,
                           socket.SOCK_STREAM)  # AF_INET is the Internet address family for IPv4. SOCK_STREAM is the socket type
    # for TCP, the protocol that will be used to transport our messages in the network
    server.connect((SERVER, PORT))


    def send(message):
        msg_send = message.encode('utf-8')
        msg_length = len(msg_send)  # msg_length is used to send the length of the message to the server.
        send_length = str(msg_length).encode('utf-8')
        send_length += b' ' * (BUFFER - len(send_length))
        server.send(send_length)
        server.send(msg_send)
        #print(server.recv(1024).decode(FORMAT))  # 64 Buffer Size is the amount of chunks i.e bytes allowed for your connection to process at a time or receive at a time.
        # here max. 64 bytes of size string is recived at a time. so if the string is more than 64 bytes then it will break the string into chunks
        # and recieve the string as stream. i.e for ex- 'Welcome to dogeyes' if 'welcome' is 64 bytes then first it will print welcome then 'to doggeyes' is
        # queued in the stream so as the recv is in the while loop it will receive the stream continuously until the string ends


    def get_clients():
        with open("client_data.json", "r") as cd:
            clients = json.load(cd)
            cd.close()
        return clients

    #Threading this function
    def c_to_c():
        inc_msg = server.recv(64).decode(FORMAT)

        if "BROADCAST" in inc_msg:

            msg_length = inc_msg.split()[1]
            msg_length = int(msg_length)
            msg_recv = server.recv(msg_length).decode(FORMAT)
            if msg_recv == "":
                print("")
            else:
                print(f"\n  BROADCASTING MESSAGE!!!\n\t==>> {msg_recv}")


        elif "INCOMING CONNECTION" in inc_msg:
            print(f"\nAn incoming connection is going to establish from {inc_msg.split()[2]}")
            connected = True

            while connected:
                if flag:
                    break

                msg_length = server.recv(BUFFER).decode(FORMAT)
                if msg_length:
                    msg_length = int(msg_length)
                    msg_recv = server.recv(msg_length).decode(FORMAT)
                    if msg_recv == "":
                        continue
                    if msg_recv.split()[0] == "DISCONNECTING":
                        print(f"\nAlert! {msg_recv} is going to disconnect")
                        break
                    else:
                        print(f"\n[{inc_msg.split()[2]}]>> {msg_recv}")

    #Check Username
    while True:
        name = input("Enter ur name: ").encode(FORMAT)
        if len(name) > 63:
            print("You are exceeding the default name length ;( please try again.")
        else:
            server.send(name)
            check_user = server.recv(64).decode(FORMAT)

            if check_user == "The username already exits, please try again.":
                print(check_user)
                pass
            else:
                print(check_user)
                break

    print(server.recv(64).decode(FORMAT)) #"Welcome to the DogEyes server!" message

    thread = threading.Thread(target=c_to_c)
    thread.start()
    flag = 0
    while True:
        con = input("Write ur message here: ")

        if con == DISCONNECTED:
            print("Thanks for joining server, see u later --w--")
            send(con)
            flag = 1
            break

        if con == "ACTIVE":
            print("Active users =>")
            for user in get_clients():
                print(user)
            continue

        if con == "CONNECT":
            print("These are the user that you can connect with:")
            time.sleep(1.5)

            for user in get_clients():
                print(user)

            c_user = input("Enter the user that you wanna chat with :")
            con=con+" "+c_user

        send(con)


except socket.error as err:
    print("socket creation failed with error %s" % (err))
