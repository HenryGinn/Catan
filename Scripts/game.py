import logging
import os
from random import shuffle

import pandas as pd
import numpy as np
from hgutilities import defaults
from hgutilities.utils import get_dict_string, make_folder, json

from Board.board import Board
from Players.player_regular import PlayerRegular
from turn import Turn
from utils import (
    get_name,
    get_change_str)
from output_state import plot_card_state
from global_variables import (
    path_data,
    path_resources,
    path_layouts,
    real_estate_graph_components)


formatter = logging.Formatter(
   "{asctime}: {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M")

splash = r"""
      ______     _____    ____________   _____        ____    ___
     /  ___/    /     |  /____   ____/  /     |      /    |  /  /
    /  /       /  /|  |      /  /      /  /|  |     /  /| | /  /
   /  /       /  /_|  |     /  /      /  /_|  |    /  / | |/  /
  /  /       /  ___   |    /  /      /  ___   |   /  /  | |  /
  \  \___   /  /   |  |   /  /      /  /   |  |  /  /   |   /
   \_____/ /__/    |__|  /__/      /__/    |__| /__/    |__/
"""
print(splash)


class Game():

    # Logging, paths, and initialisation

    def __init__(self, name=None, reset_log=True, seed=None):
        self.name = name
        self.set_paths()
        self.create_folders()
        self.init_log(reset_log)
        self.set_seed(seed)
        self.create_objects()
    
    def set_paths(self):
        self.name = get_name(self.name)
        self.path = os.path.join(
            path_data, "Games", f"{self.name}")
        self.path_logger = os.path.join(
            self.path, f"{self.name}.log")
        self.path_state = os.path.join(
            self.path, f"{self.name}State.json")

    def create_folders(self):
        make_folder(path_layouts)
        make_folder(self.path)

    def init_log(self, reset_log):
        file_handler_mode = self.get_file_handler_mode(reset_log)
        self.log = logging.getLogger(self.name)
        self.log.setLevel(logging.DEBUG)
        self.add_console_handler()
        #self.add_file_handler(file_handler_mode)
        self.log.debug(splash)
        self.log.debug(f"Initialised {self.name}")

    def get_file_handler_mode(self, reset_log):
        if reset_log is True:
            return "w+"
        else:
            return "a"

    def add_console_handler(self):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        self.log.addHandler(console_handler)

    def add_file_handler(self, file_handler_mode):
        file_handler = logging.FileHandler(
            self.path_logger, mode=file_handler_mode, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        self.log.addHandler(file_handler)

    def set_seed(self, seed):
        if seed is None:
            self.seed = np.random.randint(1, 10**6)
            self.log.debug("Numpy randomisation seed not set, generating random seed")
        else:
            self.seed = seed
            self.log.debug("Numpy randomisation seed prescribed")
        np.random.seed(self.seed)
        self.log.debug(f"Numpy randomisation seed: {np.random.seed}")

    def create_objects(self):
        self.log.info("Creating board")
        self.board = Board(self)


        
    # Saving and loading

    def save(self):
        game_state = self.get_game_state()
        with open(self.path_state, "w+") as file:
            json.dump(game_state, file, indent=2)
        self.log.info(f"Saved game at {self.path_state}")
        self.log.debug(json.dumps(self.path_state))

    def get_game_state(self):
        meta_data = self.get_meta_data()
        players_state = self.get_players_state()
        game_state = {
            "MetaData": meta_data,
            "Players": players_state}
        return game_state

    def get_players_state(self):
        players_state = {
            player.name: player.get_state()
            for player in self.players}
        return players_state

    def get_meta_data(self):
        meta_data = {
            "Layout": self.board.layout_name,
            "Colors": {player.name: player.color
                       for player in self.players},
            "Development Card Deck": self.development_deck,
            "Move": self.move,
            "Robber": self.robber_index}
        return meta_data

    def load(self):
        game_state = self.load_game_state()
        self.load_meta_data(game_state)
        self.load_player_states_from_game_state(game_state)
        self.log.info(f"Loaded state from {self.path_state}")
        self.log.debug(json.dumps(game_state))

    def load_meta_data(self, game_state):
        self.board.load_layout(game_state["MetaData"]["Layout"])
        names, colors = list(zip(*game_state["MetaData"]["Colors"].items()))
        self.initialise_players(names=names, colors=colors)
        self.development_deck = (
            game_state["MetaData"]["Development Card Deck"])
        self.move = game_state["MetaData"]["Move"]
        self.robber_index = game_state["MetaData"]["Robber"]

    def load_game_state(self):
        with open(self.path_state, "r") as file:
            game_state = json.load(file)
        return game_state

    def load_player_states_from_game_state(self, game_state):
        iterable = zip(self.players, game_state["Players"].items())
        for player, (name, player_state) in iterable:
            player.name = name
            player.set_from_state(player_state)

    def start_game(self, names=None, colors=None):
        self.initialise_players(names, colors)
        self.set_initial_states()
        self.initialise_robber()
        self.move = 0

    def initialise_players(self, names, colors):
        names = self.get_player_names(names)
        colors = self.get_player_colors(colors)
        self.players = [
            PlayerRegular(self, name, color)
            for name, color in zip(names, colors)]
        self.initialise_perspectives()

    def initialise_perspectives(self):
        for player in self.players:
            player.initialise_perspectives()

    def get_player_names(self, names):
        if names is None:
            return [1, 2, 3, 4]
        else:
            return names

    def get_player_colors(self, colors=None):
        if colors is None:
            return ["#E50000","#18E100", "#3FFF00", "#FF08FE"]
        else:
            return colors

    def set_player_colors(self, colors=None):
        colors = self.get_player_colors(colors)
        for player, color in zip(self.players, colors):
            player.color = color
            self.log.debug(f"Setting color for {player.name} to {color}")

    def set_initial_states(self):
        self.initialise_development_deck()
        self.log.info("Initialising all player states")
        for player in self.players:
            player.set_initial_states()

    def initialise_development_deck(self):
        development_path = os.path.join(
            path_resources, "Development Deck.json")
        with open(development_path, "r") as file:
            self.development_deck = json.load(file)
        shuffle(self.development_deck)
        self.log.debug(f"Initialising development deck:\n{self.development_deck}")

    def get_player(self, player_name):
        player = [
            player for player in self.players
            if player.name == player_name][0]
        return player

    def initialise_robber(self):
        robber_index = [
            index
            for index, tile in self.board.tiles
            if tile.type == "Desert"][0]
        self.update_robber(robber_index)

    def update_robber(self, index):
        self.log.info(f"Robber placed on tile {index}")
        self.robber_index = index
        self.robber_state = np.zeros(19).astype("int8")
        self.robber_state[robber_index] = 1


    # Game control

    def input_layout(self, *args, **kwargs):
        self.board.input_layout(*args, **kwargs)

    def load_layout(self, *args, **kwargs):
        self.board.load_layout(*args, **kwargs)

    def generate_layout(self, *args, **kwargs):
        self.board.generate_layout(*args, **kwargs)

    def next_turn(self):
        self.turn = Turn(self)
        self.turn.execute_dice_roll()

    def take_turn(self):
        self.turn.take_turn()

    def trade_players(self, trade):
        self.turn.trade_players_input(trade)


    # Buying real estate
    
    def buy_road(self, player_name, *args):
        """
        Attempts to buy a road for a particular player.

        Input arguments:
            player_name: name of the player attempting to buy the road
            0 additional arguments: tile_index and neighbour_index queried
            1 additional argument:  index into edge array
            3 additional arguments: tile_number, tile_order, and neighbour_index input directly
        """
        player = self.get_player(player_name)
        match len(args):
            case 0: self.buy_road_from_input(player)
            case 1: self.buy_road_from_index(player, *args)
            case 3: self.buy_road_from_indexes(player, *args)
            case _: print(f"Got {len(args)} additional args. Invalid input - see help")

    def buy_road_from_input(self, player):
        edge_indexes = self.board.get_edge_indexes()
        self.buy_road_from_indexes(player, *edge_indexes)

    def buy_road_from_indexes(self, player, *edge_indexes):
        edge_index = self.board.get_edge_index_from_indexes(*edge_indexes)
        self.buy_road_from_index(player, edge_index)

    def buy_road_from_index(self, player, edge_index):
        player.real_estate["Roads"][edge_index] = 1

    def buy_settlement(self, player_name, *args):
        """
        Attempts to buy a settlement for a particular player.

        Input arguments:
            player_name: name of the player attempting to buy the road
            0 additional arguments: tile_index and neighbour_index queried
            1 additional argument:  index into edge array
            3 additional arguments: tile_number, tile_order, and neighbour_index input directly
        """
        self.buy_vertex(player_name, "Settlements", *args)

    def buy_city(self, player_name, *args):
        """
        Attempts to buy a settlement for a particular player.

        Input arguments:
            player_name: name of the player attempting to buy the road
            0 additional arguments: tile_index and neighbour_index queried
            1 additional argument:  index into edge array
            3 additional arguments: tile_number, tile_order, and neighbour_index input directly
        """
        self.buy_vertex(player_name, "Cities", *args)

    def buy_vertex(self, player_name, vertex_type, *args):
        player = self.get_player(player_name)
        match len(args):
            case 0: self.buy_vertex_from_input(player, vertex_type)
            case 1: self.buy_vertex_from_index(player, vertex_type, *args)
            case 3: self.buy_vertex_from_indexes(player, vertex_type, *args)
            case _: print(f"Got {len(args)} additional args. Invalid input - see help")

    def buy_vertex_from_input(self, player, vertex_type):
        vertex_indexes = self.board.get_vertex_indexes()
        self.buy_vertex_from_indexes(player, vertex_type, *vertex_indexes)

    def buy_vertex_from_indexes(self, player, vertex_type, *vertex_indexes):
        vertex_index = self.board.get_vertex_index_from_indexes(*vertex_indexes)
        self.buy_vertex_from_index(player, vertex_type, vertex_index)

    def buy_vertex_from_index(self, player, vertex_type, vertex_index):
        player.real_estate[vertex_type][vertex_index] = 1

    def play_development(self, trade):
        self.turn.play_development_input(trade)


    # Updating state

    def update_state(self, card_type, actor_changes):
        self.log_update_state(card_type, actor_changes)
        for player in self.players:
            for actor, change in actor_changes.items():
                self.update_state_perspectives(
                    card_type, player, actor, change)

    def log_update_state(self, card_type, actor_changes):
        changes = {
            player.name: change
            for player, change in actor_changes.items()}
        self.log.debug(f"Updating {card_type} state for:\n{changes}")

    def update_state_perspectives(self, card_type, player, actor, change):
        for perspective in player.perspectives:
            if perspective.them is actor:
                perspective.update_state(card_type, change)
    
    
    # Output state

    def save_tiles(self):
        self.board.save_tiles()

    def show_tiles(self):
        self.board.show_tiles()

    def save_board(self):
        self.board.save_board()

    def show_board(self):
        self.board.show_board()

    def get_card_df(self):
        player_dfs = [player.get_card_df() for player in self.players]
        card_df = pd.concat(player_dfs, axis=1)
        return card_df

    def plot_card_state(self, player_name, perspective_name):
        player = self.get_player(player_name)
        perspective = player.get_perspective(perspective_name)
        plot_card_state(perspective)

    def __str__(self):
        card_df = self.get_card_df()
        string = card_df.to_string()
        return string
