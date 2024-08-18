from os.path import join

from hgutilities.utils import json
import numpy as np
import pandas as pd


class Trade():

    def __init__(self, catan):
        self.catan = catan
        self.load_costs()

    def load_costs(self):
        path = join(self.catan.path_resources, "Costs.json")
        with open(path, "r") as file:
            self.costs = json.load(file)


    # Converting trade inputs into complete trade dictionaries

    def __call__(self, trade):
        self.trade_states = self.get_trade_states_from_input(trade)

    def get_trade_states_from_input(self, trade):
        trade = self.preprocess_trade_from_input(trade)
        trade_states = self.get_trade_states(trade)
        return trade_states

    def preprocess_trade_from_input(self, trade):
        for player_name, player_trade in trade.items():
            player_trade = self.add_missing_keys(player_trade)
            player_trade = self.convert_road_notation(player_trade)
            player_trade = self.subtract_real_estate_costs(player_trade)
            player_trade = self.subtract_development_costs(player_trade)
            trade[player_name] = player_trade
        return trade

    def add_missing_keys(self, player_trade):
        player_trade = self.add_missing_card_keys(player_trade)
        player_trade = self.add_missing_real_estate_keys(player_trade)
        return player_trade

    def add_missing_card_keys(self, player_trade):
        for card_type in self.catan.card_trade_types:
            if card_type not in player_trade:
                player_trade.update({card_type: 0})
        return player_trade

    def add_missing_real_estate_keys(self, player_trade):
        for real_estate in self.catan.real_estate_types:
            if real_estate not in player_trade:
                player_trade.update({real_estate: []})
        return player_trade

    def convert_road_notation(self, player_trade):
        roads = [edge.get_vectors() for edge in self.catan.board.edges
                 for trade_edge in player_trade["Roads"]
                 if edge.get_midpoint() == trade_edge]
        player_trade["Roads"] = roads
        return player_trade

    def subtract_real_estate_costs(self, player_trade):
        for real_estate in self.catan.real_estate_types:
            for resource, price in self.costs[real_estate].items():
                total_price = price * len(player_trade[real_estate])
                player_trade[resource] -= total_price
        return player_trade

    def subtract_development_costs(self, player_trade):
        for resource, price in self.costs["Development"].items():
            player_trade[resource] -= price*player_trade["Development"]
        return player_trade

    def output(self, trade):
        print("")
        print(pd.DataFrame(trade).to_string())


    # Converting trade dictionaries into trade states

    def get_trade_states(self, trade):
        trade_states = {player_name:
            self.get_trade_state_from_trade(
                trade, self.catan.get_player(player_name))
            for player_name in trade}
        return trade_states

    def get_trade_state_from_trade(self, trade, player):
        trade_real_estate = self.get_trade_real_estate(trade, player)
        trade_state = {**trade_real_estate}
        return trade_state

    def get_trade_real_estate(self, trade, player):
        trade_real_estate = {
            "Settlements": self.get_settlements(trade, player),
            "Cities": self.get_cities(trade, player),
            "Roads": self.get_roads(trade, player)}
        return trade_real_estate

    def get_settlements(self, trade, player):
        settlements = self.catan.board.get_vertex_state(
            trade[player.name]["Settlements"])
        settlements = settlements | player.settlement_state
        return settlements

    def get_cities(self, trade, player):
        cities = self.catan.board.get_vertex_state(
            trade[player.name]["Cities"])
        cities = cities | player.city_state
        return cities

    def get_roads(self, trade, player):
        roads = self.catan.board.get_edge_state(
            trade[player.name]["Roads"])
        roads = roads | player.road_state
        return roads

    def output_states(self, states):
        string = "\n\n".join(self.catan.get_state_string(state)
                             for state in states)
        return string
















    
