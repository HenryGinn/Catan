import pandas as pd

from Cards.card_resource import CardResource
from Cards.card_victory import CardVictory
from Cards.card_monopoly import CardMonopoly
from Cards.card_knight import CardKnight
from Cards.card_harvest import CardHarvest
from Cards.card_road import CardRoad


class Player():

    player_type = "General"
    resource_types = ["Wheat", "Sheep", "Wood", "Ore", "Mud"]
    development_types = [
        CardVictory,
        CardMonopoly,
        CardKnight,
        CardHarvest,
        CardRoad]

    def __init__(self, players, ID):
        self.players = players
        self.ID = ID
        self.initialise_attributes()

    def initialise_attributes(self):
        resources = self.get_initial_resources()
        developments = self.get_initial_developement()
        self.cards = resources + developments

    def get_initial_resources(self):
        resource_cards = [CardResource(self, resource)
                          for resource in self.resource_types]
        return resource_cards

    def get_initial_developement(self):
        development_cards = [Development(self)
            for Development in self.development_types]
        return development_cards

    def get_cards_dataframe(self):
        card_dict = self.get_card_dict()
        df = pd.DataFrame(card_dict).set_index("Name")
        indexes = [[self.name, self.name], df.columns.values]
        df.columns = pd.MultiIndex.from_arrays(
            indexes, names=("Player", "Amount"))
        df.index.name = None
        return df

    def get_card_dict(self):
        card_data = list(zip(*[(card.name, card.min, card.max)
                               for card in self.cards]))
        card_dict = {key: value_list for key, value_list in zip(
            ["Name", "Min", "Max"], card_data)}
        return card_dict
