import json
import os
import socket
from _thread import *
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = 'localhost'
port = 5555

server_ip = socket.gethostbyname(server)

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

s.listen(4)
print("Waiting for a connection")

currentId = 0
config_file = os.path.abspath(os.path.dirname(__file__)) + '\configuration.json'
with open(config_file) as file:
    game_data = json.load(file)

def threaded_client(conn):
    global currentId, game_data
    conn.send(str.encode(str(currentId)))
    game_data[str(currentId)]["connected"] = True
    currentId += 1
    reply = ''
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode('utf-8')
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                print("Recieved: " + reply)
                jreply = json.loads(reply)
                game_data[str(jreply["id"])] = jreply

                reply = json.dumps(game_data)
                print("Sending: " + reply)

            conn.sendall(str.encode(reply))
        except:
            break

    print("Connection Closed")
    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)

    start_new_thread(threaded_client, (conn,))