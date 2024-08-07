from os.path import join, dirname

from hgutilities import defaults
from hgutilities.utils import make_folder

from Board.board import Board
from Players.player_regular import PlayerRegular


class Catan():

    def __init__(self, **kwargs):
        defaults.kwargs(self, kwargs)
        self.set_main_paths()
        self.create_folders()
        self.create_objects()

    def set_main_paths(self):
        self.path_base = dirname(dirname(__file__))
        self.path_data = join(self.path_base, "Data")
        self.path_resources = join(self.path_data, "Resources")
        self.path_layouts = join(self.path_data, "Layouts")
        self.path_games = join(self.path_data, "Games")

    def create_folders(self):
        make_folder(self.path_layouts)
        make_folder(self.path_games)

    def create_objects(self):
        self.board = Board(self)
        self.initialise_players()

    def initialise_players(self):
        self.players = [PlayerRegular(self, index)
                        for index in range(4)]
