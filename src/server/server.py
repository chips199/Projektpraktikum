import datetime
import json
import os
import socket
from _thread import start_new_thread
import sys
import random
import string
from copy import copy


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
number_of_players_per_game = 3
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
config_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', r'game\\configuration.json'))
with open(config_file) as file:
    game_data = json.load(file)

game_datas = list()
for _ in range(number_of_games_at_a_time):
    game_datas.append(copy(game_data))
# 0 = not connected, 1 = connected, 2 = connection lost
players_connected = [[0] * number_of_players_per_game] * number_of_games_at_a_time
# to convert list of game data and ids to dict
game_data_dict = dict(zip(get_random_ids(number_of_games_at_a_time, 4), game_datas))


def threaded_client(conn):
    global currentGId, currentPId, game_data_dict, players_connected, game_data
    # send realtive game and player id
    this_gid = copy(currentGId)
    this_pid = copy(currentPId)
    conn.send(str.encode(str(this_gid) + ',' + str(this_pid)))
    # get real game_id
    game_id = list(game_data_dict.keys())[this_gid]
    # set player status in game_data to online
    game_data_dict[game_id][str(this_pid)]["connected"] = True
    players_connected[this_gid][this_pid] = 1
    # increase player id and if necessary game id for the next connection
    currentPId += 1
    if currentPId == number_of_players_per_game:
        currentGId += 1
        if currentGId == number_of_games_at_a_time:
            currentGId = 0
        currentPId = 0
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
                jreply = json.loads(reply)
                game_data_dict[game_id][str(jreply["id"])] = jreply
                reply = json.dumps(game_data_dict[game_id])

            conn.sendall(str.encode(reply))
            last_msg = datetime.datetime.now()
        except:
            break
        if (datetime.datetime.now() - last_msg).seconds > 5:
            print("Connection timeout")
            break

    print("Connection Closed")
    # set lost player to connected false and disconected
    game_data_dict[game_id][str(this_pid)]["connected"] = True
    players_connected[this_gid][this_pid] = 2
    conn.close()
    # check if there is a game where every player connected once but disconnected again, if true reset the game
    if players_connected[this_gid].count(2) == number_of_players_per_game:
        players_connected[this_gid] = [0] * number_of_players_per_game
        # print(game_data)
        game_data_dict[game_id] = copy(game_data)
        for n in range(number_of_players_per_game):
            game_data_dict[game_id][str(n)]["connected"] = False
        print("game zurückgesetzt da alle spieler diconnected sind")


while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)
    start_new_thread(threaded_client, (conn,))
