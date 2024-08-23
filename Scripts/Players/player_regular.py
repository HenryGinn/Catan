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
        self.set_initial_geometry_state()
        for perspective in self.perspectives:
            perspective.card_state = zeros(len(self.catan.card_lookup))

    def set_initial_geometry_state(self):
        self.geometry_state = {
            "Settlements": zeros(len(self.catan.board.vertices)),
            "Cities": zeros(len(self.catan.board.vertices)),
            "Roads": zeros(len(self.catan.board.edges))}

    def get_state(self):
        perspective_states = self.get_perspective_states()
        state = {**self.geometry_state,
                 **perspective_states}
        return state

    def get_perspective_states(self):
        perspective_states = {
            perspective.name: perspective.card_state
            for perspective in self.perspectives}
        return perspective_states

    def update_state(self, state):
        self.load_geometry_from_state(state)
        self.load_perspectives_from_state(state)

    def load_geometry_from_state(self, state):
        self.geometry_state = {
            key: array(state[key])
            for key in ["Settlements", "Cities", "Roads"]}
    
    def load_perspectives_from_state(self, state):
        for perspective in self.perspectives:
            perspective.card_state = array(state[perspective.name])

    def get_perspective_state(self, player_name):
        perspective = [persective for perspective in self.perspectives
                       if perspective.name == player_name][0]
        return perspective.card_state


    # Output

    def __str__(self):
        state = self.get_state()
        string = self.catan.get_state_string(state)
        return string
