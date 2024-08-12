from pandas import concat

from Players.player import Player
from Players.player_perspective import PlayerPerspective


class PlayerRegular(Player):

    player_type = "Regular"

    def __init__(self, catan, ID):
        super().__init__(catan, ID)
        self.name = f"{self.ID + 1}"
        self.initialise_player_perspectives()

    def initialise_player_perspectives(self):
        self.perspectives = [
            PlayerPerspective(index, self)
            for index in range(4)]

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
        self.road_state = [False
            for edge in self.catan.board.edges]
