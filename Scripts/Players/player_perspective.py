from Players.player import Player


class PlayerPerspective(Player):

    player_type = "Perspective"

    def __init__(self, perspective, base):
        name = f"{base.name} view {perspective.name}"
        self.view = f"{perspective.name}"
        super().__init__(base.catan, name)
        self.player = base

    def initialise_card_state(self):
        self.card_state = {f"{card_type} {bound}": 0
                           for card_type in self.catan.card_data
                           for bound in ["Min", "Max"]}
