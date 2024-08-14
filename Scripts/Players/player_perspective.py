from pandas import DataFrame, MultiIndex

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

    def get_card_df(self):
        card_dict = self.get_card_dict()
        card_df = DataFrame(card_dict).set_index("Card")
        card_df = self.set_card_df_multi_index(card_df)
        return card_df

    def get_card_dict(self):
        card_dict = [{"Card": card,
                      "Min": self.card_state[f"{card} Min"],
                      "Max": self.card_state[f"{card} Max"]}
                     for card in card_types]
        return card_dict

    def set_card_df_multi_index(self, card_df):
        indexes = [[self.name, self.name], card_df.columns.values]
        card_df.columns = MultiIndex.from_arrays(
            indexes, names=("Player", "Amount"))
        return card_df
