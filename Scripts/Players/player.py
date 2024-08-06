from Cards.card_victory import CardVictory
from Cards.card_monopoly import CardMonopoly
from Cards.card_knight import CardKnight
from Cards.card_harvest import CardHarvest
from Cards.card_road import CardRoad


class Player():

    player_type = "General"
    resource = ["Wheat", "Sheep", "Wood", "Ore", "Mud"]
    development_card_classes = [
        CardVictory,
        CardMonopoly,
        CardKnight,
        CardHarvest,
        CardRoad

    def __init__(self, players, ID):
        self.players = players
        self.ID = ID
        self.initialise_attributes()

    def initialise_attributes(self):
        self.initialise_resources()
        self.initialise_developement()

    def initialise_resources(self):
        self.resource_cards = [
            CardResource(self, resource)
            for resource in self.resources]

    def initialise_developement(self):
        self.development_cards = [
            Development(self)
            for Development in developement_card_classes)
