import datetime
import json
import math
import os
import platform
import socket
from _thread import start_new_thread
import random
import string
import copy
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
number_of_games_at_a_time = 1
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
# game_datas = list()
# for _ in range(number_of_games_at_a_time):
#     game_datas.append(copy(game_data))
# game_data_dict = dict(zip(get_random_ids(number_of_games_at_a_time, 4), game_datas))
game_data_dict = dict()
for gid in get_random_ids(number_of_games_at_a_time, 4):
    # game_data_dict[gid] = copy(game_data)
    game_data_dict[gid] = copy.deepcopy(game_data)

# generate a dict with the games and info if each slot is used, with different stati
# # 0 = not connected, 1 = connected in lobby, 2 = connection lost, 3 = after game started
players_connected = dict()
empty_game = [0] * number_of_players_per_game
for k in game_data_dict.keys():
    players_connected[k] = copy.deepcopy(empty_game)
# [[0,0,0,0][0,0,0,0][0,0,0,0]]

print(game_data_dict)
print(spawn_points)
print(players_connected)


def game_server(game_id, this_gid):
    """
        provides metadata with the start and end of a game as well as spawning and despawning items
    """
    global game_data_dict
    # wait until game starts or exit if lobby was closed
    # while not players_connected[this_gid].__contains__(3):
    while not players_connected[game_id].__contains__(3):
        # if players_connected[this_gid].count(0) == number_of_players_per_game:
        if players_connected[game_id].count(0) == number_of_players_per_game:
            exit(0)
        pass
    # reset items of the game, to be sure
    game_data_dict[game_id]["metadata"]["spawnpoints"]["items"] = {"Sword": [],
                                                                   "Laser": []
                                                                   }
    # set sstart and end time
    game_data_dict[game_id]["metadata"]["start"] = (datetime.datetime.now() + datetime.timedelta(seconds=12)).strftime(
        "%d/%m/%Y, %H:%M:%S")
    game_data_dict[game_id]["metadata"]["end"] = (datetime.datetime.now() + datetime.timedelta(seconds=312)).strftime(
        "%d/%m/%Y, %H:%M:%S")
    # deal with items while the game runs
    last_w_of_p = [None] * number_of_players_per_game
    last_spawn_check = datetime.datetime.now()
    # while players_connected[this_gid].count(3) > 0:
    while players_connected[game_id].count(3) > 0:
        # get the weapon of each player
        # tmp = copy(list(game_data_dict[game_id].items()))
        tmp = list(game_data_dict[game_id].items())
        w_of_p = list(map(lambda x: x[1]["weapon_data"][3],  # type: ignore[no-any-return]
                          filter(lambda y: ["0", "1", "2", "3"].__contains__(y[0]),
                                 tmp)))
        # if the weapon of a player has changed, delete the collected weapon in items
        for ip, wp in enumerate(w_of_p):
            p_pos = game_data_dict[game_id][str(ip)]["position"]
            if last_w_of_p[ip] != wp:
                last_w_of_p[ip] = wp
                if wp != "Fist":
                    potential_items = game_data_dict[game_id]["metadata"]["spawnpoints"]["items"][wp]
                    potential_items_distances = list(map(lambda x: math.dist(p_pos, x), potential_items))
                    i = potential_items_distances.index(min(potential_items_distances))
                    game_data_dict[game_id]["metadata"]["spawnpoints"]["items"][wp].pop(i)
        # every 10sec spawn new items
        if datetime.datetime.now() - last_spawn_check > datetime.timedelta(seconds=10):
            last_spawn_check = datetime.datetime.now()
            # go through every spawn-point as tuple
            for point in spawn_points[game_data_dict[game_id]["metadata"]["map"]]["item_spawnpoints"]:
                free = True
                # check if the point is free
                for ki, vi in game_data_dict[game_id]["metadata"]["spawnpoints"]["items"].items():
                    if vi.__contains__(point):
                        free = False
                # go through every item odds
                for k, v in spawn_points[game_data_dict[game_id]["metadata"]["map"]]["item-odds"].items():
                    r = random.random()
                    # if the current point is free and the random is beneath the odd append the item.
                    if r < v and free:
                        game_data_dict[game_id]["metadata"]["spawnpoints"]["items"][k].append(point)
                        break


def reset_games():
    """
        checks each game if a game has been used and rests them after it isn't used anymore
    """
    for i, g in players_connected.items():
        # going through all games
        if g.count(0) == number_of_players_per_game:
            # set all players to not connected
            players_connected[i] = [0] * number_of_players_per_game
            # get session_id and set game_data to default and reset map
            game_id = i
            game_data_dict[game_id] = copy.deepcopy(game_data)
            game_data_dict[game_id]["metadata"]["scoreboard"] = {"0": [0, 0],
                                                                 "1": [0, 0],
                                                                 "2": [0, 0],
                                                                 "3": [0, 0]}
            game_data_dict[game_id]["metadata"]["map"] = "none"
            # game_data_dict does not reset online, so manually reset it
            for n in range(number_of_players_per_game):
                game_data_dict[game_id][str(n)]["connected"] = False
                game_data_dict[game_id][str(n)]["killed_by"] = [0, 0, 0, 0]
            print(f"{i} reset, because no player was there anymore")


def threaded_client(conn):
    """
        handles a connection to a client from creating/joining a lobby up to the game loop and disconnections
    """
    global game_data_dict, players_connected  # , maps_dict
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
        # if players_connected[local_gid].count(0) == 4:
        if players_connected[start_msg].count(0) == 4:
            # send error Message if session hasn't been opened
            conn.send(str.encode("5, Session isn't opened"))
            conn.close()
            exit(1)
        elif players_connected[start_msg].count(3) > 0:
            # rejoin if possible test phase ----------------------------------------
            if 0 < players_connected[start_msg].count(0) < 4:
                this_gid = local_gid
                this_pid = players_connected[start_msg].index(0)
                players_connected[start_msg][this_pid] = 1
            # rejoin if possible test phase ----------------------------------------
            # send error Message if session is running
            # conn.send(str.encode("5, Session is already running"))
            # conn.close()
            # exit(1)
        elif 0 < players_connected[start_msg].count(0) < 4:
            # connects player if there is space
            this_gid = local_gid
            this_pid = players_connected[start_msg].index(0)
            players_connected[start_msg][this_pid] = 1
        elif players_connected[start_msg].count(0) == 4:
            # send error Message if session is full
            conn.send(str.encode("5, Session is full"))
            conn.close()
            exit(1)
        else:
            # send error Message if session is full
            conn.send(str.encode("5, An unexpected Error occurred"))
            conn.close()
            exit(1)
        # setting a few necessary variables
        game_id = start_msg
        # this_spawn_points = copy(spawn_points[maps_dict[game_id]])
        this_spawn_points = copy.deepcopy(spawn_points[game_data_dict[game_id]["metadata"]["map"]])
        conn.send(str.encode(f"{this_pid},{game_id}"))
        print(f"Joined Lobby: {game_id}")
        # finished connecting player
    else:
        # Create new game
        try:
            map_name = start_msg
            # this_spawn_points = copy(spawn_points[map_name])
            this_spawn_points = copy.deepcopy(spawn_points[map_name])
        except KeyError:
            # send error Message if map is not known, means the user entered sth other than 4 digits
            conn.send(str.encode("5, Invalid Session_ID"))
            conn.close()
            exit(1)
        # search for empty games
        game_found = False
        this_gid = -9999
        this_pid = -9999
        for i, g in players_connected.items():
            if g.count(0) == number_of_players_per_game:
                # if empty game found set first player as connected
                this_gid = list(game_data_dict.keys()).index(i)
                this_pid = 0
                players_connected[i][0] = 1
                game_found = True
                break
        # send error Message if no empty game exists
        if not game_found:
            # send msg if no empty game can be found
            conn.send(str.encode("5, No Lobby available try again later"))
            conn.close()
            exit(1)
        # get real game_id
        game_id = list(game_data_dict.keys())[this_gid]
        print(game_id)
        start_new_thread(game_server, (game_id, this_gid,))
        game_data_dict[game_id]["metadata"]["map"] = map_name
        game_data_dict[game_id]["metadata"]["spawnpoints"] = this_spawn_points
        conn.send(str.encode(f"{this_pid},{game_id}"))
        print(f"Lobby starts: {game_id}")
        # finished creating game and booking player

    # reuniting join and create game
    start_waiting = datetime.datetime.now()
    last_msg = datetime.datetime.now()
    while True:
        try:
            msg = conn.recv(2048).decode()
        except ConnectionResetError:
            # handles if the connection is lost
            print("connection lost")
            players_connected[game_id][this_pid] = 0
            reset_games()
            conn.close()
            exit(0)
        if players_connected[game_id][this_pid] != 1 and players_connected[game_id][this_pid] != 3:
            # handles if the lobby is reset, can happen if the admin has disconnected
            print("Lobby was reseted")
            conn.send(str.encode("Lobby was deleted"))
            reset_games()
            conn.close()
            exit(0)
        if msg == "lobby_check":
            # sends back how many players are connected to the lobby
            conn.send(str.encode(f"{players_connected[game_id].count(1)}"))
            last_msg = datetime.datetime.now()
        elif msg == "game started":
            # sends True if a game was started by another Player
            conn.sendall(str.encode(str(players_connected[game_id][this_pid] == 3)))
            print(this_gid, this_pid, str.encode(str(players_connected[game_id][this_pid] == 3)))
        elif msg == "get_spawnpoints":
            # sends spownpoints and data for velocity
            conn.sendall(str.encode(json.dumps(this_spawn_points)))
            last_msg = datetime.datetime.now()
        elif msg == "get Mapname":
            # sends the name of the selected map
            conn.send(str.encode(game_data_dict[game_id]["metadata"]["map"]))
        elif msg == "ready":
            # starts the game and sends name of the map
            conn.send(str.encode(game_data_dict[game_id]["metadata"]["map"]))
            print(game_data_dict[game_id]["metadata"]["map"])
            players_connected[game_id] = list(map(lambda x: 3 if x == 1 or x == 3 else 0, players_connected[game_id]))
            print(this_gid, this_pid, players_connected)
            break
        elif msg == "get max players":
            # sends the maximum amount of players
            conn.send(str.encode(f"{number_of_players_per_game}"))
            last_msg = datetime.datetime.now()
        elif (datetime.datetime.now() - start_waiting).seconds > 600:
            # ends the lobby after 10min
            print("Lobby expired")
            players_connected[game_id] = [2] * number_of_players_per_game
            reset_games()
            conn.close()
            exit(0)
        elif (datetime.datetime.now() - last_msg).seconds > 2:
            # open up a connection if somebody leaves or has a disconnect
            print("connection timeout")
            players_connected[game_id][this_pid] = 0
            reset_games()
            conn.close()
            exit(0)

        sleep(0.2)

    print("Game starts: " + game_id)
    # set player status in game_data to online
    game_data_dict[game_id][str(this_pid)]["connected"] = True
    # enter game loop
    while True:
        try:
            # receive data from client
            data = conn.recv(2048).decode('utf-8')
            # if no data has been sent the connection has been closed
            if data:
                # parse the client data into the game_data Dictionary, and send the result back to the client
                game_data_dict[game_id][str(this_pid)] = json.loads(data)
                deaths = game_data_dict[game_id][str(this_pid)]["killed_by"]
                kills = list(map(lambda x: x[1]["killed_by"][:4],  # type: ignore[no-any-return]
                                 list(filter(lambda x: x[0] != "metadata", game_data_dict[game_id].items()))))
                for k, v in enumerate(zip(*kills)):
                    game_data_dict[game_id]["metadata"]["scoreboard"][str(k)][0] = sum(v)
                game_data_dict[game_id]["metadata"]["scoreboard"][str(this_pid)][1] = sum(deaths)
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
            # if the last message is more than 5 seconds old theconnection timedout
            print("Connection timeout")
            break

    print("Connection Closed")
    # set lost player to connected false and disconected and close the connection
    game_data_dict[game_id][str(this_pid)]["connected"] = False
    players_connected[game_id][this_pid] = 0
    conn.close()
    # check if there is a game where every player connected once but disconnected again, if true reset the game
    reset_games()


while True:
    # constantly accept new connection, and start a new thread to handle the connection
    conn, addr = s.accept()
    print("Connected to: ", addr)
    start_new_thread(threaded_client, (conn,))
