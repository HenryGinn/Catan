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
    real_estate)


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
        self.add_file_handler(file_handler_mode)
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
        players_state = {player.name: player.get_state()
                         for player in self.players}
        game_state = {"MetaData": meta_data,
                      "Players": players_state}
        return game_state

    def get_meta_data(self):
        meta_data = {
            "Layout": self.board.layout_name,
            "Colors": {player.name: player.color
                       for player in self.players},
            "Development Card Deck": self.development_deck,
            "Move": self.move}
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


    # Game control

    def next_turn(self):
        self.turn = Turn(self)
        self.turn.execute_dice_roll()

    def take_turn(self):
        self.turn.take_turn()

    def trade_players(self, trade):
        self.turn.trade_players_input(trade)
    
    def trade_assets(self, trade):
        self.turn.trade_assets_input(trade)

    def play_development(self, trade):
        self.turn.play_development_input(trade)

    def update_state(self, card_type, actor_changes):
        self.log_update_state(card_type, actor_changes)
        for player in self.players:
            for actor, change in actor_changes.items():
                for perspective in player.perspectives:
                    if perspective.them is actor:
                        perspective.update_state(card_type, change)

    def log_update_state(self, card_type, actor_changes):
        changes = {
            player.name: change
            for player, change in actor_changes.items()}
        self.log.debug(f"Updating {card_type} state for:\n{changes}")


    # Output state

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
