import os
from random import shuffle

from pandas import DataFrame, MultiIndex, concat
import numpy as np
from hgutilities import defaults
from hgutilities.utils import get_dict_string, make_folder, json

from Board.board import Board
from Players.player_regular import PlayerRegular
from Trades.turn import Turn
from utils import get_name
from output_state import plot_card_state
from global_variables import (
    path_data,
    path_resources,
    path_layouts,
    real_estate,
    state_indexes)

class Catan():

    def __init__(self, name=None):
        self.name = name
        self.set_path_game()
        self.create_folders()
        self.create_objects()

    def set_path_game(self):
        self.name = get_name(self.name)
        self.path_game = os.path.join(
            path_data, "Games", f"{self.name}.json")

    def create_folders(self):
        make_folder(path_layouts)
        make_folder(os.path.dirname(self.path_game))

        
    # Saving and loading

    def save(self):
        game_state = self.get_game_state()
        with open(self.path_game, "w+") as file:
            json.dump(game_state, file, indent=2)

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
            "Moves": self.moves}
        return meta_data

    def load(self):
        game_state = self.load_game_state()
        self.load_meta_data(game_state)
        self.load_player_states_from_game_state(game_state)

    def load_meta_data(self, game_state):
        self.board.load_layout(game_state["MetaData"]["Layout"])
        names, colors = list(zip(*game_state["MetaData"]["Colors"].items()))
        self.initialise_players(names=names, colors=colors)
        self.development_deck = (
            game_state["MetaData"]["Development Card Deck"])
        self.moves = game_state["MetaData"]["Moves"]

    def load_game_state(self):
        with open(self.path_game, "r") as file:
            game_state = json.load(file)
        return game_state

    def load_player_states_from_game_state(self, game_state):
        iterable = zip(self.players, game_state["Players"].items())
        for player, (name, player_state) in iterable:
            player.name = name
            player.update_state(player_state)


    # Players and state manipulations

    def create_objects(self):
        self.board = Board(self)

    def start_game(self, names=None, colors=None):
        self.initialise_players(names, colors)
        self.set_initial_states()
        self.moves = -1

    def initialise_players(self, names, colors):
        names = self.get_player_names(names)
        colors = self.get_player_colors(colors)
        self.players = [PlayerRegular(self, name, color)
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

    def set_initial_states(self):
        self.initialise_development_deck()
        for player in self.players:
            player.set_initial_states()

    def initialise_development_deck(self):
        development_path = os.path.join(
            path_resources, "Development Deck.json")
        with open(development_path, "r") as file:
            self.development_deck = json.load(file)
        shuffle(self.development_deck)

    def get_player(self, player_name):
        player = [
            player for player in self.players
            if player.name == player_name][0]
        return player

    def next_turn(self):
        self.turn = Turn(self)

    def take_turn(self):
        self.turn.take_turn()

    def trade_players(self, trade):
        self.turn.trade_players_input(trade)
    
    def trade_assets(self, trade):
        self.turn.trade_assets_input(trade)

    def play_development(self, trade):
        self.turn.play_development_input(trade)


    # Output state

    def get_state_string(self, state):
        geometry_string = self.get_geometry_string(state)
        card_df = self.get_card_df(state)
        string = (f"{geometry_string}\n\n"
                  f"{card_df.to_string()}")
        return string

    def get_geometry_string(self, state):
        geometry_string = get_dict_string({
            key: self.board.get_string(state[key], structure)
            for key, structure in real_estate.items()})
        return geometry_string

    def get_card_df(self, state):
        perspective_dfs = [
            self.get_perspective_df(name, state[name])
            for name in state if name not in real_estate]
        card_df = concat(perspective_dfs, axis=1)
        return card_df

    def get_perspective_df(self, name, card_state):
        df = {
            (card_type, index): card_state[card_slice][index]
            for card_type, card_slice in state_indexes.items()
            for index in range(min(132, card_slice.stop) - card_slice.start)}
        df = DataFrame({name: df})
        df.index = df.index.set_names(("Card Type", "Count"))
        return df

    def plot_card_state(self, player_name, perspective_name):
        player = self.get_player(player_name)
        perspective = player.get_perspective(perspective_name)
        plot_card_state(perspective)
