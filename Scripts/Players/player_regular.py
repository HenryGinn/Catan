from pandas import concat

from Players.player import Player
from Players.player_perspective import PlayerPerspective


class PlayerRegular(Player):

    player_type = "Regular"

    def __init__(self, players, ID):
        super().__init__(players, ID)
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
        pass
