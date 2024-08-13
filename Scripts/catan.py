from os.path import join, dirname
import json

from hgutilities import defaults
from hgutilities.utils import make_folder

from Board.board import Board
from Players.player_regular import PlayerRegular
from Trades.trade import Trade
from utils import get_name


class Catan():

    def __init__(self, name=None, **kwargs):
        self.name = name
        defaults.kwargs(self, kwargs)
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
        self.initialise_players()
        self.trade = Trade(self)

    def initialise_players(self):
        self.players = [PlayerRegular(self, index)
                        for index in range(4)]

    def set_initial_states(self):
        for player in self.players:
            player.set_initial_states()

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
