from pandas import concat
from pandas import DataFrame
from hgutilities.utils import get_dict_string

from Players.player import Player
from Players.player_perspective import PlayerPerspective


class PlayerRegular(Player):

    player_type = "Regular"

    def initialise_perspectives(self):
        self.perspectives = [
            PlayerPerspective(player.name, self)
            for player in self.catan.players]

    def set_initial_states(self):
        self.set_initial_board_state()
        for perspective in self.perspectives:
            perspective.initialise_card_state()

    def set_initial_board_state(self):
        self.set_initial_settlement_state()
        self.set_initial_city_state()
        self.set_initial_road_state()

    def set_initial_settlement_state(self):
        self.state_settlement = [False
            for vertex in self.catan.board.vertices]

    def set_initial_city_state(self):
        self.state_city = [False
            for vertex in self.catan.board.vertices]

    def set_initial_road_state(self):
        self.state_road = [False
            for edge in self.catan.board.edges]

    def get_state_dict(self):
        geometry_dict = self.get_geometry_dict()
        perspectives_dict = self.get_perspectives_dict()
        state_dict = {"Geometry": geometry_dict,
                      "Perspectives": perspectives_dict}
        return state_dict

    def get_geometry_dict(self):
        geometry_dict = {"Settlements": self.state_settlement,
                         "Cities": self.state_city,
                         "Roads": self.state_road}
        return geometry_dict

    def get_perspectives_dict(self):
        perspectives_dict = {
            perspective.name: perspective.card_state
            for perspective in self.perspectives}
        return perspectives_dict

    def load_state_from_player_state(self, player_state):
        self.load_from_geometry_dict(player_state["Geometry"])
        self.load_from_perspectives_dict(player_state["Perspectives"])

    def load_from_geometry_dict(self, geometry_dict):
        self.settlement_state = geometry_dict["Settlements"]
        self.city_state = geometry_dict["Cities"]
        self.road_state = geometry_dict["Roads"]

    def load_from_perspectives_dict(self, card_states):
        iterable = zip(self.perspectives, card_states.items())
        for perspective, (name, card_state) in iterable:
            perspective.name = name
            perspective.card_state = card_state


    # Output

    def __str__(self):
        geometry_data = self.get_geometry_data()
        card_df = self.get_card_df()
        string = (f"{get_dict_string(geometry_data)}\n\n"
                  f"{card_df.to_string()}")
        return string

    def get_geometry_data(self):
        board = self.catan.board
        geometry_data = {
            "Settlements": ", ".join(board.vertex_list(self.state_settlement)),
            "Cities": ", ".join(board.vertex_list(self.state_city)),
            "Roads": ", ".join(board.edge_list(self.state_road))}
        return geometry_data

    def get_card_df(self):
        perspective_dfs = [perspective.get_card_df()
                           for perspective in self.perspectives]
        card_df = concat(perspective_dfs, axis=1)
        return card_df
