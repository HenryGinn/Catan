from pandas import DataFrame, MultiIndex

from Players.player import Player


class PlayerPerspective(Player):

    player_type = "Perspective"

    def __init__(self, ID, player_base):
        super().__init__(player_base.catan, ID)
        self.player_base = player_base
        self.name = f"{self.player_base.name} view {self.ID + 1}"

    def initialise_card_state(self):
        resource_card_state = self.get_initial_resources()
        development_card_state = self.get_initial_developments()
        self.card_state = {
            **resource_card_state, **development_card_state}

    def get_initial_resources(self):
        resource_card_state = {f"{resource} {bound}": 0
                               for resource in resource_types
                               for bound in ["Min", "Max"]}
        return resource_card_state

    def get_initial_developments(self):
        development_card_state = {f"{development} {bound}": 0
                                  for development in development_types
                                  for bound in ["Min", "Max"]}
        return development_card_state

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


resource_types = ["Wheat", "Sheep", "Wood", "Ore", "Mud"]
development_types = ["Knight", "Victory", "Monopoly", "RoadBuilder", "Harvest"]
card_types = resource_types + development_types
