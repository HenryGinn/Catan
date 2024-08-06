from Players.player import Player


class PlayerPerspective(Player):

    player_type = "Perspective"

    def __init__(self, ID, player_base):
        super().__init__(player_base.players, ID)
        self.player_base = player_base
