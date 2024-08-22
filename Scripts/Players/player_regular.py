from numpy import array, zeros

from Players.player import Player
from Players.player_perspective import PlayerPerspective


class PlayerRegular(Player):

    player_type = "Regular"

    def __init__(self, catan, name, color):
        super().__init__(catan, name)
        self.color = color

    def initialise_perspectives(self):
        self.perspectives = [
            PlayerPerspective(player, self)
            for player in self.catan.players]
        self.set_self_perspective()

    def set_self_perspective(self):
        self.self_perspective = [
            perspective for perspective in self.perspectives
            if perspective.view is self.name][0]

    def set_initial_states(self):
        self.set_initial_board_state()
        for perspective in self.perspectives:
            perspective.initialise_card_state()

    def set_initial_board_state(self):
        self.settlement_state = zeros(len(self.catan.board.vertices)).astype("bool")
        self.city_state = zeros(len(self.catan.board.vertices)).astype("bool")
        self.road_state = zeros(len(self.catan.board.edges)).astype("bool")

    def get_state(self):
        geometry_state = self.get_geometry_state()
        perspectives_state = self.get_perspectives_state()
        state = {"Geometry": geometry_state,
                 "Perspectives": perspectives_state}
        return state

    def get_geometry_state(self):
        geometry_state = {
            "Settlements": self.settlement_state,
            "Cities": self.city_state,
            "Roads": self.road_state}
        return geometry_state

    def get_perspectives_state(self):
        perspectives_state = {
            perspective.name: perspective.card_state
            for perspective in self.perspectives}
        return perspectives_state

    def update_state(self, player_state):
        self.load_from_geometry_dict(player_state["Geometry"])
        self.load_from_perspectives_dict(player_state["Perspectives"])

    def load_from_geometry_dict(self, geometry_dict):
        self.settlement_state = array(geometry_dict["Settlements"]).astype("bool")
        self.city_state = array(geometry_dict["Cities"]).astype("bool")
        self.road_state = array(geometry_dict["Roads"]).astype("bool")

    def load_from_perspectives_dict(self, card_states):
        iterable = zip(self.perspectives, card_states.items())
        for perspective, (name, card_state) in iterable:
            perspective.name = name
            perspective.card_state = card_state

    def get_perspective_state(self, player_name):
        perspective = [persective for perspective in self.perspectives
                       if perspective.name == player_name][0]
        return perspective.card_state

    # Output

    def __str__(self):
        state = self.get_state()
        string = self.catan.get_state_string(state)
        return string
