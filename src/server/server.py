import datetime
import json
import os
import socket
from _thread import start_new_thread
import sys
import random
import string

from src.game import game


def get_random_ids(number_of_ids, length):
    # returns a string of integers dealing as an id for the games
    res = list()
    while len(res) < number_of_ids:
        letters = string.digits
        result_str = ''.join(random.choice(letters) for i in range(length))
        if not res.__contains__(result_str):
            res.append(str(result_str))
    # print("Random string of length", length, "is:", result_str)
    return res


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

number_of_games_at_a_time = 1
number_of_players_per_game = 4
server = 'localhost'
port = 5555

server_ip = socket.gethostbyname(server)

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

s.listen(number_of_games_at_a_time * number_of_players_per_game)
print("Waiting for a connection")
currentGId, currentPId = 0, 0
config_file = os.path.abspath(os.path.dirname()) + r'\configuration.json'
with open(config_file) as file:
    game_data = json.load(file)

game_datas = [game_data] * number_of_games_at_a_time
players_connected = [[False] * number_of_players_per_game] * number_of_games_at_a_time
# to convert list of game data and ids to dict
game_data_dict = dict(zip(get_random_ids(number_of_games_at_a_time, 4), game_datas))


def threaded_client(conn):
    global currentGId, currentPId, game_data_dict, players_connected
    conn.send(str.encode(str(currentGId) + ',' + str(currentPId)))
    game_id = game_data_dict.keys()[str(currentGId)]
    game_data_dict[game_id][str(currentPId)]["connected"] = True
    # game_data[str(currentPId)]["connected"] = True
    currentPId += 1
    if currentPId == number_of_players_per_game:
        currentGId += 1
        if currentGId == number_of_games_at_a_time:
            currentGId = 0
        currentPId = 0
    players_connected[currentGId][currentPId] = True
    reply = ''
    last_msg = datetime.datetime.now()
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode('utf-8')
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                #print("Recieved: " + reply)
                jreply = json.loads(reply)
                game_data_dict[game_id][str(jreply["id"])] = jreply

                reply = json.dumps(game_data_dict[game_id])
                #print("Sending: " + reply)
            conn.sendall(str.encode(reply))
        except:
            break
        if datetime.datetime.now() - last_msg > 5:
            print("Connection lost")
            break

    print("Connection Closed")
    game_data_dict[str(currentGId)][str(currentPId)]["connected"] = None
    conn.close()
    # check if there is a game where every player connected once but disconnected again, if true reset the game
    for g in players_connected:
        if g.count(None) == number_of_players_per_game:
            g = [False] * number_of_players_per_game


while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)
    start_new_thread(threaded_client, (conn,))
