from Players.player import Player


class PlayerPerspective(Player):

    player_type = "Perspective"

    def __init__(self, ID, player_base):
        super().__init__(player_base.players, ID)
        self.player_base = player_base
        self.name = f"{self.player_base.name} view {self.ID + 1}"

    def __str__(self):
        return self.get_cards_dataframe().to_string()
