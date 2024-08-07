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
            for index in range(4) if index != self.ID]

    def get_cards_dataframe_views(self):
        df_self = self.get_cards_dataframe()
        df_views = [perspective.get_cards_dataframe()
                    for perspective in self.perspectives]
        df = concat([df_self, *df_views], axis=1)
        return df

    def __str__(self):
        df = self.get_cards_dataframe_views()
        return df.to_string()
