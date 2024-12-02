from os.path import join, dirname

from pandas import DataFrame, MultiIndex, concat
import numpy as np
from hgutilities import defaults
from hgutilities.utils import get_dict_string, make_folder, json

from Board.board import Board
from Players.player_regular import PlayerRegular
from Trades.trade import Trade
from utils import get_name


class Catan():

    real_estate = {
        "Settlements": "Vertex",
        "Cities": "Vertex",
        "Roads": "Edge"}

    def __init__(self, name=None):
        self.name = name
        self.set_main_paths()
        self.create_folders()
        self.load_resources()
        self.create_objects()

    def set_main_paths(self):
        self.path_base = dirname(dirname(__file__))
        self.path_data = join(self.path_base, "Data")
        self.path_resources = join(self.path_data, "Resources")
        self.path_layouts = join(self.path_data, "Layouts")
        self.set_path_game()

    def set_path_game(self):
        self.name = get_name(self.name)
        self.path_game = join(self.path_data,
                              "Games", f"{self.name}.json")

    def create_folders(self):
        make_folder(self.path_layouts)
        make_folder(dirname(self.path_game))

    def load_resources(self):
        self.load_card_types()
        self.load_card_lookup()

        
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
            "Development Card Deck": self.trade.development_deck}
        return meta_data

    def load(self):
        game_state = self.load_game_state()
        self.load_meta_data(game_state)
        self.load_player_states_from_game_state(game_state)
        self.add_random_cards_to_card_data()

    def load_meta_data(self, game_state):
        self.board.load_layout(game_state["MetaData"]["Layout"])
        names, colors = list(zip(*game_state["MetaData"]["Colors"].items()))
        self.initialise_players(names=names, colors=colors)
        self.trade.development_deck = (
            game_state["MetaData"]["Development Card Deck"])

    def load_game_state(self):
        with open(self.path_game, "r") as file:
            game_state = json.load(file)
        return game_state

    def load_player_states_from_game_state(self, game_state):
        iterable = zip(self.players, game_state["Players"].items())
        for player, (name, player_state) in iterable:
            player.name = name
            player.update_state(player_state)

    def load_card_types(self):
        self.load_card_data()
        self.set_resource_cards()
        self.set_card_types_tradable()
        self.set_ownable_development_cards()

    def load_card_data(self):
        path = join(self.path_resources, "Card Data.json")
        with open(path, "r") as file:
            self.card_data = json.load(file)

    def add_random_cards_to_card_data(self):
        for index, player in enumerate(self.players):
            card_name = f"Random {player.name}"
            self.card_data.update({card_name:
                {"Type": "Special", "Count": np.inf,
                 "Tradable": True, "Ownable": False}})
            self.card_lookup.update({card_name: index})

    def set_resource_cards(self):
        self.resources = [
            card for card in self.card_data
            if self.card_data[card]["Type"] == "Resource"]

    def set_card_types_tradable(self):
        self.tradables = [
            card for card in self.card_data
            if self.card_data[card]["Tradable"]]

    def set_ownable_development_cards(self):
        self.developments = [
            card for card in self.card_data
            if self.card_data[card]["Type"] == "Development"]

    def load_card_lookup(self):
        path = join(self.path_resources, "Card Lookup.json")
        with open(path, "r") as file:
            self.card_lookup = json.load(file)


    # Players and state manipulations

    def create_objects(self):
        self.board = Board(self)
        self.trade = Trade(self)

    def initialise_players(self, names=None, colors=None):
        names = self.get_player_names(names)
        colors = self.get_player_colors(colors)
        self.players = [PlayerRegular(self, name, color)
                        for name, color in zip(names, colors)]
        self.add_random_cards_to_card_data()
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
        for player in self.players:
            player.set_initial_states()

    def get_player(self, player_name):
        player = [player for player in self.players
                  if player.name == player_name][0]
        return player


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
            for key, structure in self.real_estate.items()})
        return geometry_string

    def get_card_df(self, state):
        perspective_dfs = [
            self.get_perspective_df(name, state[name])
            for name in state if name not in self.real_estate]
        card_df = concat(perspective_dfs, axis=1)
        return card_df

    def get_perspective_df(self, name, card_state):
        card_dict = dict(zip(self.card_lookup, card_state))
        keys_and_values = zip(["Card", name], zip(*card_dict.items()))
        card_df = {key: value for key, value in keys_and_values}
        perspective_df = DataFrame(card_df).set_index("Card")
        return perspective_df
    
    def o(self):
        print(self.trade.output_states(self.trade.trade_states))
