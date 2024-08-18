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
            PlayerPerspective(player.name, self)
            for player in self.catan.players]

    def set_initial_states(self):
        self.set_initial_board_state()
        for perspective in self.perspectives:
            perspective.initialise_card_state()

    def set_initial_board_state(self):
        self.settlement_state = zeros(len(self.catan.board.vertices))
        self.city_state = zeros(len(self.catan.board.vertices))
        self.road_state = zeros(len(self.catan.board.edges))

    def get_state_dict(self):
        geometry_dict = self.get_geometry_dict()
        perspectives_dict = self.get_perspectives_dict()
        state_dict = {"Geometry": geometry_dict,
                      "Perspectives": perspectives_dict}
        return state_dict

    def get_geometry_dict(self):
        geometry_dict = {"Settlements": self.settlement_state,
                         "Cities": self.city_state,
                         "Roads": self.road_state}
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
        self.settlement_state = array(geometry_dict["Settlements"])
        self.city_state = array(geometry_dict["Cities"])
        self.road_state = array(geometry_dict["Roads"])

    def load_from_perspectives_dict(self, card_states):
        iterable = zip(self.perspectives, card_states.items())
        for perspective, (name, card_state) in iterable:
            perspective.name = name
            perspective.card_state = card_state


    # Output

    def __str__(self):
        state = self.get_state_dict()
        string = self.catan.get_state_string(state)
        return string
