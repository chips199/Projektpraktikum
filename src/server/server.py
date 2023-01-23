import datetime
import json
import os
import socket
from _thread import start_new_thread
import sys
import random
import string
from copy import copy
from itertools import repeat
from time import sleep
from typing import List


def get_random_ids(number_of_ids, length):
    # returns a string of integers dealing as an id for the games
    res: list[str] = list()
    while len(res) < number_of_ids:
        letters = string.digits
        result_str = ''.join(random.choice(letters) for i in range(length))
        if not res.__contains__(result_str):
            res.append(str(result_str))
    # print("Random string of length", length, "is:", result_str)
    return res


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

number_of_games_at_a_time = 1
number_of_players_per_game = 2
server = 'localhost'
port = 5556

server_ip = socket.gethostbyname(server)

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

s.listen(number_of_games_at_a_time * number_of_players_per_game)
print("Waiting for a connection")

config_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', r'game\\configuration.json'))
with open(config_file) as file:
    game_data = json.load(file)

spawn_file = os.path.abspath(os.path.join(os.path.dirname(__file__), r'spawnpoints.json'))
with open(spawn_file) as sfile:
    spawn_points = json.load(sfile)

game_datas = list()
for _ in range(number_of_games_at_a_time):
    game_datas.append(copy(game_data))
# 0 = not connected, 1 = connected, 2 = connection lost
players_connected = [[0] * number_of_players_per_game] * number_of_games_at_a_time
# to convert list of game data and ids to dict
game_data_dict = dict(zip(get_random_ids(number_of_games_at_a_time, 4), game_datas))
maps_dict = dict(zip(game_data_dict.keys(), repeat("none")))


def reset_games():
    for i, g in enumerate(players_connected):
        print(g)
        if g.count(2) + g.count(0) == number_of_players_per_game:
            players_connected[i] = [0] * number_of_players_per_game
            game_id = list(game_data_dict.keys())[i]
            game_data_dict[game_id] = copy(game_data)
            maps_dict[game_id] = "none"
            for n in range(number_of_players_per_game):
                game_data_dict[game_id][str(n)]["connected"] = False
            print("game zurückgesetzt da alle spieler diconnected sind")


def threaded_client(conn):
    global game_data_dict, players_connected, maps_dict
    start_msg = conn.recv(2048).decode()
    print(start_msg)
    # splitting create game and join
    if len(start_msg) == 4:
        # join lobby
        # join player to lobby and return id
        try:
            local_gid = list(game_data_dict.keys()).index(start_msg)
        except ValueError:
            # send error Message if session does not exist
            conn.send(str.encode("5, Session ID does not exist"))
            conn.close()
            exit(1)
        if players_connected[local_gid].count(0) == 4:
            # send error Message if session is full
            conn.send(str.encode("5, Session isn't opened"))
            conn.close()
            exit(1)
        elif players_connected[local_gid].count(2) == 4:
            # send error Message if session is full
            conn.send(str.encode("5, Session is already running"))
            conn.close()
            exit(1)
        elif 0 < players_connected[local_gid].count(0) < 4:
            this_gid = local_gid
            this_pid = players_connected[this_gid].index(0)
            players_connected[this_gid][this_pid] = 1
        else:
            # send error Message if session is full
            conn.send(str.encode("5, Session is full"))
            conn.close()
            exit(1)
        game_id = start_msg
        this_spawn_points = copy(spawn_points[maps_dict[game_id]])
        conn.send(str.encode(f"{this_pid},{game_id}"))
        # finished connecting player
    else:
        # Create new game
        try:
            map_name = start_msg
            this_spawn_points = copy(spawn_points[map_name])
        except KeyError:
            # send error Message if map is not known
            conn.send(str.encode("5, Map does not exist"))
            conn.close()
            exit(1)
        # search for empty games
        game_found = False
        this_gid = -9999
        this_pid = -9999
        for i, g in enumerate(players_connected):
            print(g)
            if g.count(0) == number_of_players_per_game:
                # if empty game found set first player as connected
                this_gid = i
                this_pid = 0
                players_connected[this_gid][0] = 1
                game_found = True
                break
        # send error Message if no empty game exists
        if not game_found:
            conn.send(str.encode("5, Server is full"))
            conn.close()
            exit(1)
        print(this_gid)
        # get real game_id
        game_id = list(game_data_dict.keys())[this_gid]
        maps_dict[game_id] = start_msg
        conn.send(str.encode(f"{this_pid},{game_id}"))
        # finished creating game and booking player

    # reuniting join and create game
    start_waiting = datetime.datetime.now()
    last_msg = datetime.datetime.now()
    while True:
        try:
            msg = conn.recv(2048).decode()
        except ConnectionResetError:
            print("connection lost")
            players_connected[this_gid][this_pid] = 2
            reset_games()
            conn.close()
            exit(0)
        print(msg)
        if players_connected[this_gid][this_pid] != 1:
            print("Lobby was reseted")
            conn.send(str.encode("Lobby was deleted"))
            reset_games()
            conn.close()
            exit(0)
        if msg == "lobby_check":
            conn.send(str.encode(f"{players_connected[this_gid].count(1)}"))
            last_msg = datetime.datetime.now()
        elif msg == "get_spawnpoints":
            conn.sendall(str.encode(json.dumps(this_spawn_points)))
            last_msg = datetime.datetime.now()
        elif msg == "get Mapname":
            conn.send(str.encode(maps_dict[game_id]))
        elif msg == "ready":
            conn.send(str.encode(maps_dict[game_id]))
            # set all not connected players to disconnected, to make sure that reset_game() sees this lobby as done after all players disconnected
            for n, p in enumerate(players_connected[this_gid]):
                if p == 0:
                    players_connected[this_gid][n] = 2
            break
        elif msg == "get max players":
            conn.send(str.encode(f"{number_of_players_per_game}"))
            last_msg = datetime.datetime.now()
        elif (datetime.datetime.now() - start_waiting).seconds > 600:
            print("Lobby expired")
            players_connected[this_gid] = [2] * number_of_players_per_game
            reset_games()
            conn.close()
            exit(0)
        elif (datetime.datetime.now() - last_msg).seconds > 10:
            print("connection lost")
            players_connected[this_gid][this_pid] = 2
            reset_games()
            conn.close()
            exit(0)
        print(f"Waiting for players in {game_id}")
        sleep(1)

    print("Game starts")
    # set player status in game_data to online
    game_data_dict[game_id][str(this_pid)]["connected"] = True
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
    reset_games()


while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)
    start_new_thread(threaded_client, (conn,))
