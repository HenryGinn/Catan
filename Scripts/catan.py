from os.path import join, dirname

from pandas import DataFrame, MultiIndex, concat
from hgutilities import defaults
from hgutilities.utils import get_dict_string, make_folder, json

from Board.board import Board
from Players.player_regular import PlayerRegular
from Trades.trade import Trade
from utils import get_name


class Catan():

    resource_types = ["Wheat",
                      "Sheep",
                      "Wood",
                      "Ore",
                      "Mud"]
    development_types = ["Knight",
                         "Victory",
                         "Monopoly",
                         "RoadBuilder",
                         "Harvest"]
    card_types = resource_types + development_types
    card_trade_types = resource_types + ["Development"]
    real_estate_types = ["Settlements", "Cities", "Roads"]

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
        self.path_game = join(self.path_data,
                              "Games", f"{self.name}.json")

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

    def get_player(self, player_name):
        player = [player for player in self.players
                  if player.name == player_name][0]
        return player


    # Saving and loading

    def save(self):
        game_state = self.get_game_state()
        with open(self.path_game, "w+") as file:
            json.dump(game_state, file, indent=2)

    def get_game_state(self):
        players_state = {player.name: player.get_state()
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


    # Output state

    def get_state_string(self, state):
        geometry_string = self.get_geometry_string(state["Geometry"])
        card_df = self.get_card_df(state["Perspectives"])
        string = (f"{geometry_string}\n\n"
                  f"{card_df.to_string()}")
        return string

    def get_geometry_string(self, geometry_state):
        settlement, city, road = list(geometry_state.values())
        geometry_string = get_dict_string({
            "Settlements": self.board.get_vertex_string(settlement),
            "Cities"     : self.board.get_vertex_string(city),
            "Roads"      : self.board.get_edge_string(road)})
        return geometry_string

    def get_card_df(self, card_state):
        perspective_dfs = [
            self.get_perspective_df(name, perspective_state)
            for name, perspective_state in card_state.items()]
        card_df = concat(perspective_dfs, axis=1)
        return card_df

    def get_perspective_df(self, name, perspective_state):
        perspective_dict = self.get_perspective_dict(perspective_state)
        perspective_df = DataFrame(perspective_dict).set_index("Card")
        perspective_df = self.set_df_multi_index(name, perspective_df)
        return perspective_df

    def get_perspective_dict(self, perspective_state):
        perspective_dict = [
            {"Card": card,
             "Min": perspective_state[f"{card} Min"],
             "Max": perspective_state[f"{card} Max"]}
            for card in self.card_types]
        return perspective_dict

    def set_df_multi_index(self, name, perspective_df):
        indexes = [[name, name], perspective_df.columns.values]
        perspective_df.columns = MultiIndex.from_arrays(
            indexes, names=("Player", "Amount"))
        return perspective_df
