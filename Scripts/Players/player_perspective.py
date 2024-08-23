from Players.player import Player


class PlayerPerspective(Player):

    player_type = "Perspective"

    def __init__(self, perspective, base):
        name = f"{base.name} view {perspective.name}"
        self.view = f"{perspective.name}"
        super().__init__(base.catan, name)
        self.base = base
