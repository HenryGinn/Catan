from Players.player import Player
from Players.player_perspective import PlayerPerspective


class PlayerRegular(Player):

    player_type = "Regular"

    def __init__(self, players, ID):
        super().__init__(players, ID)
        self.initialise_player_perspectives()

    def initialise_player_perspectives(self):
        self.perspectives = [
            PlayerPerspective(index, self)
            for index in range(4) if index != self.ID]
