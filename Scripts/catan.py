from os.path import join, dirname
import json

from hgutilities import defaults
from hgutilities.utils import make_folder

from Board.board import Board
from Players.player_regular import PlayerRegular
from Trades.trade import Trade
from utils import get_name


class Catan():

    def __init__(self, name=None):
        self.name = name
        self.set_main_paths()
        self.create_folders()
        self.create_objects()

    def set_main_paths(self):
        self.path_base = dirname(dirname(__file__))
        self.path_data = join(self.path_base, "Data")
        self.path_resources = join(self.path_data, "Resources")
        self.path_layouts = join(self.path_data, "Layouts")
        self.set_path_game()

    def set_path_game(self):
        self.name = get_name(self.name)
        self.path_game = join(self.path_data, "Games", self.name)

    def create_folders(self):
        make_folder(self.path_layouts)
        make_folder(dirname(self.path_game))

    def create_objects(self):
        self.board = Board(self)
        self.trade = Trade(self)

    def initialise_players(self, names=None, colors=None):
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
        for player in self.players:
            player.set_initial_states()


    # Saving and loading

    def save(self):
        game_state = self.get_game_state()
        with open(self.path_game, "w+") as file:
            json.dump(game_state, file, indent=2)

    def get_game_state(self):
        players_state = {player.name: player.get_state_dict()
                         for player in self.players}
        game_state = {"Layout": self.board.layout_name,
                      "Players": players_state}
        return game_state

    def load(self):
        self.initialise_players()
        game_state = self.load_game_state()
        self.board.load_layout(game_state["Layout"])
        self.load_player_states_from_game_state(game_state)

    def load_game_state(self):
        with open(self.path_game, "r") as file:
            game_state = json.load(file)
        return game_state

    def load_player_states_from_game_state(self, game_state):
        iterable = zip(self.players, game_state["Players"].items())
        for player, (name, player_state) in iterable:
            player.name = name
            player.load_state_from_player_state(player_state)
