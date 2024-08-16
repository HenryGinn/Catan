from Players.player import Player


class PlayerPerspective(Player):

    player_type = "Perspective"

    def __init__(self, perspective_name, player_base):
        name = f"{player_base.name} view {perspective_name}"
        super().__init__(player_base.catan, name)
        self.player_base = player_base

    def initialise_card_state(self):
        self.card_state = {f"{card_type} {bound}": 0
                           for card_type in self.catan.card_type
                           for bound in ["Min", "Max"]}
