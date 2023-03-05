import datetime
import json
import math
import os
import platform
import socket
from _thread import start_new_thread
import random
import string
from copy import copy
from itertools import repeat
from time import sleep
from typing import List, Any


def get_random_ids(number_of_ids, length):
    """
        generates a lsit of random code, string of ids
    :param number_of_ids: length of the generated list : integer
    :param length: length of each code : integer
    :return: the list of strings
    """
    # initiate the result as empty list of strings
    res: list[str] = list()
    # to prevent two identical ids, loop as long as not enough are generated
    while len(res) < number_of_ids:
        # define the set out of which the string is created
        letters = string.digits
        # generat a String
        result_str = ''.join(random.choice(letters) for i in range(length))
        # check if the string is a duplicate
        if not res.__contains__(result_str):
            res.append(str(result_str))
    return res


# create socket server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# set number of maximal parallel games that can be opened, and how many players can play in each.
number_of_games_at_a_time = 3
number_of_players_per_game = 4
# Localhost for tunneling with ngrok, for local hosting
server = 'localhost'
port = 5556

# set host and port of server
try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

# regulates how many parallel connections are allowed
s.listen(number_of_games_at_a_time * number_of_players_per_game)
print("Waiting for a connection")
# load the config file as basis for a fresh game
seperator = "\\" if platform.system() == 'Windows' else "/"
config_file = seperator.join(
    list(os.path.abspath(os.path.dirname(__file__)).split(seperator)[
         :-1])) + f"{seperator}gamelogic{seperator}configuration.json"
# print("\\".join(list(os.path.abspath(os.path.dirname(__file__)).split("\\")[:-1])) + "\\game\\configuration.json")
with open(config_file) as file:
    game_data = json.load(file)
# load spawn points
spawn_file = os.path.abspath(os.path.join(os.path.dirname(__file__), r'spawnpoints.json'))
with open(spawn_file) as sfile:
    spawn_points = json.load(sfile)
# generate list of games and put them with the ids in a dictionary
game_datas = list()
for _ in range(number_of_games_at_a_time):
    game_datas.append(copy(game_data))
game_data_dict = dict(zip(get_random_ids(number_of_games_at_a_time, 4), game_datas))
# generate a 2d list with the games and info if each slot is used, with different stati
# 0 = not connected, 1 = connected in lobby, 2 = connection lost, 3 = after game started
players_connected: list[Any] = list()
for _ in range(number_of_games_at_a_time):
    players_connected.append([0] * number_of_players_per_game)
# get a dict to save the map of each lobby
maps_dict = dict(zip(game_data_dict.keys(), repeat("none")))


def game_server(game_id, this_gid):
    global game_data_dict
    while not players_connected[this_gid].__contains__(3) and players_connected[this_gid].count(
            0) != number_of_players_per_game:
        pass
    game_data_dict[game_id]["metadata"]["start"] = (datetime.datetime.now() + datetime.timedelta(seconds=10)).strftime(
        "%d/%m/%Y, %H:%M:%S")
    game_data_dict[game_id]["metadata"]["end"] = (datetime.datetime.now() + datetime.timedelta(seconds=310)).strftime(
        "%d/%m/%Y, %H:%M:%S")
    # print(game_data_dict[game_id]["metadata"]["start"], game_data_dict[game_id]["metadata"]["end"])
    # exit(0)
    last_w_of_p = [None] * number_of_players_per_game
    last_spawn_check = None
    while players_connected[this_gid] != [0] * number_of_players_per_game:
        # print(game_data_dict[game_id])
        tmp = copy(list(game_data_dict[game_id].items()))
        # print(tmp)
        w_of_p = list(map(lambda x: x[1]["weapon_data"][3],
                          filter(lambda y: ["0", "1", "2", "3"].__contains__(y[0]),
                                 tmp)))
        # print(game_data_dict[game_id].items())
        for ip, wp in enumerate(w_of_p):
            p_pos = game_data_dict[game_id][str(ip)]["position"]
            if last_w_of_p[ip] != wp:
                last_w_of_p[ip] = wp
                if wp != "Fist":
                    potential_items = game_data_dict[game_id]["metadata"]["spawnpoints"]["items"][wp]
                    potential_items_distances = list(map(lambda x: math.dist(p_pos, x), potential_items))
                    i = potential_items_distances.index(min(potential_items_distances))
                    game_data_dict[game_id]["metadata"]["spawnpoints"]["items"][wp].pop(i)
        if last_spawn_check is None or datetime.datetime.now() - last_spawn_check > datetime.timedelta(seconds=10):
            last_spawn_check = datetime.datetime.now()
            for point in spawn_points[maps_dict[game_id]]["item_spawnpoints"]:
                free = True
                for ki, vi in game_data_dict[game_id]["metadata"]["spawnpoints"]["items"].items():
                    if vi.__contains__(point):
                        free = False
                for k, v in spawn_points[maps_dict[game_id]]["item-odds"].items():
                    r = random.random()
                    print(r)
                    if r < v and free:
                        game_data_dict[game_id]["metadata"]["spawnpoints"]["items"][k].append(point)
                        break


def reset_games():
    """
        checks each game if a game has been used and rests them after it isn't used anymore
    """
    for i, g in enumerate(players_connected):
        # going through all games
        if g.count(2) + g.count(0) == number_of_players_per_game and g.count(2) > 0:
            # set all players to not connected
            players_connected[i] = [0] * number_of_players_per_game
            # get session_id and set game_data to default and reset map
            game_id = list(game_data_dict.keys())[i]
            game_data_dict[game_id] = copy(game_data)
            game_data_dict[game_id]["metadata"]["scoreboard"] = {"0": [0, 0],
                                                                 "1": [0, 0],
                                                                 "2": [0, 0],
                                                                 "3": [0, 0]}
            maps_dict[game_id] = "none"
            # game_data_dict does not reset online, so manually reset it
            for n in range(number_of_players_per_game):
                game_data_dict[game_id][str(n)]["connected"] = False
                game_data_dict[game_id][str(n)]["killed_by"] = [0, 0, 0, 0]
            print(f"{list(game_data_dict.keys())[i]} reset, because no player was there anymore")


def threaded_client(conn):
    global game_data_dict, players_connected, maps_dict
    # receiving the first message
    start_msg = conn.recv(2048).decode()
    print(start_msg)

    # splitting create game and join, if the code is 4 digits long, try connecting, else try creating a new game
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
            # send error Message if session hasn't been opened
            conn.send(str.encode("5, Session isn't opened"))
            conn.close()
            exit(1)
        elif players_connected[local_gid].count(3) > 1:
            # send error Message if session is running
            conn.send(str.encode("5, Session is already running"))
            conn.close()
            exit(1)
        elif 0 < players_connected[local_gid].count(0) < 4:
            # connects player if there is space
            this_gid = local_gid
            this_pid = players_connected[this_gid].index(0)
            players_connected[this_gid][this_pid] = 1
        else:
            # send error Message if session is full
            conn.send(str.encode("5, Session is full"))
            conn.close()
            exit(1)
        # setting a few necessary variables
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
            # send error Message if map is not known, means the user entered sth other than 4 digits
            conn.send(str.encode("5, Invalid Session_ID"))
            conn.close()
            exit(1)
        # search for empty games
        game_found = False
        this_gid = -9999
        this_pid = -9999
        for i, g in enumerate(players_connected):
            if g.count(0) == number_of_players_per_game:
                # if empty game found set first player as connected
                this_gid = i
                this_pid = 0
                players_connected[this_gid][0] = 1
                game_found = True
                break
        # send error Message if no empty game exists
        if not game_found:
            # send msg if no empty game can be found
            conn.send(str.encode("5, Server is full"))
            conn.close()
            exit(1)
        # get real game_id
        game_id = list(game_data_dict.keys())[this_gid]
        start_new_thread(game_server, (game_id, this_gid,))
        game_data_dict[game_id]["metadata"]["map"] = start_msg
        game_data_dict[game_id]["metadata"]["spawnpoints"] = this_spawn_points
        maps_dict[game_id] = start_msg
        conn.send(str.encode(f"{this_pid},{game_id}"))
        # finished creating game and booking player

    # reuniting join and create game
    print(f"Lobby starts: {game_id}")
    start_waiting = datetime.datetime.now()
    last_msg = datetime.datetime.now()
    while True:
        try:
            msg = conn.recv(2048).decode()
        except ConnectionResetError:
            # handles if the connection is lost
            print("connection lost")
            players_connected[this_gid][this_pid] = 2
            reset_games()
            conn.close()
            exit(0)
        if players_connected[this_gid][this_pid] != 1 and players_connected[this_gid][this_pid] != 3:
            # handles if the lobby is reset, can happen if the admin has disconnected
            print("Lobby was reseted")
            conn.send(str.encode("Lobby was deleted"))
            reset_games()
            conn.close()
            exit(0)
        if msg == "lobby_check":
            conn.send(str.encode(f"{players_connected[this_gid].count(1)}"))
            last_msg = datetime.datetime.now()
        elif msg == "game started":
            conn.sendall(str.encode(str(players_connected[this_gid][this_pid] == 3)))
        elif msg == "get_spawnpoints":
            conn.sendall(str.encode(json.dumps(this_spawn_points)))
            last_msg = datetime.datetime.now()
        elif msg == "get Mapname":
            conn.send(str.encode(maps_dict[game_id]))
        elif msg == "ready":
            conn.send(str.encode(maps_dict[game_id]))
            players_connected[this_gid] = list(map(lambda x: 3 if x == 1 else 2, players_connected[this_gid]))
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
        elif (datetime.datetime.now() - last_msg).seconds > 2:
            print("connection timeout")
            players_connected[this_gid][this_pid] = 0
            reset_games()
            conn.close()
            exit(0)
        # elif msg == "":
        #     print("connection lost")
        #     players_connected[this_gid][this_pid] = 0
        #     reset_games()
        #     conn.close()
        #     exit(0)

        sleep(0.2)

    print("Game starts: " + game_id)
    # set player status in game_data to online
    game_data_dict[game_id][str(this_pid)]["connected"] = True
    # enter game loop
    while True:
        try:
            # receive data from client
            data = conn.recv(2048).decode('utf-8')
            reply = data
            # if no data has been sent the connection has been closed
            if data:
                # print(reply)
                # parse the client data into the game_data Dictionary, and send the result back to the client
                game_data_dict[game_id][str(this_pid)] = json.loads(reply)
                # print(game_data_dict[game_id][this_pid])
                deaths = game_data_dict[game_id][str(this_pid)]["killed_by"]
                kills = list(map(lambda x: x[1]["killed_by"][:4],  # type: ignore[no-any-return]
                                 list(filter(lambda x: x[0] != "metadata", game_data_dict[game_id].items()))))
                for k, v in enumerate(zip(*kills)):
                    game_data_dict[game_id]["metadata"]["scoreboard"][str(k)][0] = sum(v)
                game_data_dict[game_id]["metadata"]["scoreboard"][str(this_pid)][1] = sum(deaths)
                # print(game_data_dict[game_id])
                conn.sendall(str.encode(json.dumps(game_data_dict[game_id])))
                # to track how often the client sends a message track the time
                last_msg = datetime.datetime.now()
            else:
                conn.send(str.encode("Goodbye"))
                break
        except:
            # if the connection doesn't exist anymore break the loop
            break
        if (datetime.datetime.now() - last_msg).seconds > 5:
            # if the last message is more than 5 seconds old the connection timedout
            print("Connection timeout")
            break

    print("Connection Closed")
    # set lost player to connected false and disconected and close the connection
    game_data_dict[game_id][str(this_pid)]["connected"] = False
    players_connected[this_gid][this_pid] = 2
    conn.close()
    # check if there is a game where every player connected once but disconnected again, if true reset the game
    reset_games()


while True:
    # constantly accept new connection, and start a new thread to handle the connection
    conn, addr = s.accept()
    print("Connected to: ", addr)
    start_new_thread(threaded_client, (conn,))
