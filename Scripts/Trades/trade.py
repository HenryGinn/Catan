from hgutilities.utils import json
import numpy as np
import pandas as pd

from Trades.development import Development
from global_variables import (
    path_resources)


class Trade(Development):

    def __init__(self, catan):
        self.catan = catan
        self.load_costs()

    def load_costs(self):
        path = os.path.join(path_resources, "Costs.json")
        with open(path, "r") as file:
            self.costs = json.load(file)


    # Converting trade inputs into complete trade dictionaries

    def __call__(self, trade):
        self.trade_states = self.get_trade_states_from_input(trade)
        self.execute_trade(self.trade_states)

    def get_trade_states_from_input(self, trade):
        self.preprocess_trade_from_input(trade)
        trade_states = self.get_trade_states(trade)
        return trade_states

    def preprocess_trade_from_input(self, trade):
        self.add_missing_players(trade)
        for player_name, player_trade in trade.items():
            self.add_missing_keys(player_trade)
            self.convert_road_notation(player_trade)
            self.subtract_real_estate_costs(player_trade)
            self.subtract_development_costs(player_trade)
            self.convert_resource_keys(player_trade)
            trade[player_name] = player_trade

    def add_missing_players(self, trade):
        for player in self.catan.players:
            if player.name not in trade:
                trade.update({player.name: {}})

    def add_missing_keys(self, player_trade):
        self.add_missing_card_keys(player_trade)
        self.add_missing_real_estate_keys(player_trade)

    def add_missing_card_keys(self, player_trade):
        for card_type in self.catan.card_data:
            if card_type not in player_trade:
                player_trade.update({card_type: 0})

    def add_missing_real_estate_keys(self, player_trade):
        for real_estate in self.catan.real_estate:
            if real_estate not in player_trade:
                player_trade.update({real_estate: []})

    def convert_road_notation(self, player_trade):
        roads = [edge.get_vectors() for edge in self.catan.board.edges
                 for trade_edge in player_trade["Roads"]
                 if edge.get_midpoint() == trade_edge]
        player_trade["Roads"] = roads

    def subtract_real_estate_costs(self, player_trade):
        for real_estate in self.catan.real_estate:
            for resource, price in self.costs[real_estate].items():
                total_price = price * len(player_trade[real_estate])
                player_trade[resource] -= total_price

    def subtract_development_costs(self, player_trade):
        for resource, price in self.costs["Development"].items():
            player_trade[resource] -= price*player_trade["Development"]

    def convert_resource_keys(self, player_trade):
        for resource, data in self.catan.card_data.items():
            if data["Type"] == "Resource":
                for bound in ["Min", "Max"]:
                    player_trade.update({f"{resource} {bound}":
                                         player_trade[resource]})
                del player_trade[resource]

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
        trade_state = {
            **self.get_trade_real_estate(trade, player),
            **self.get_trade_perspectives(trade, player)}
        return trade_state

    def get_trade_real_estate(self, trade, player):
        trade_real_estate = {
            real_estate_type: self.get_real_estate(
                trade, player, real_estate_type)
            for real_estate_type in self.catan.real_estate}
        return trade_real_estate

    def get_real_estate(self, trade, player, real_estate_type):
        real_estate = self.catan.board.get_state(
            trade[player.name][real_estate_type], real_estate_type)
        existing_real_estate = player.geometry_state[real_estate_type]
        real_estate = real_estate | existing_real_estate
        return real_estate

    def get_trade_perspectives(self, trade, player):
        trade_perspectives = {
            perspective.name: self.get_trade_perspective(
                trade, player, perspective)
            for perspective in player.perspectives}
        return trade_perspectives

    def get_trade_perspective(self, trade, player, perspective):
        trade_function = trade_functions[player == perspective.base]
        return self.get_trade_perspective_self(
            trade, perspective, trade_function)

    def get_trade_perspective_self(self, trade, perspective, trade_function):
        card_state = [
            trade_function(trade[perspective.view][card],
                           perspective.card_state[index])
            for card, index in self.catan.card_lookup.items()]
        return card_state

    def execute_trade(self, trade_states):
        self.pick_up_developments(trade_states)
        for player_name, trade_state in trade_states.items():
            player = self.catan.get_player(player_name)
            player.update_state(trade_state)

    def pick_up_developments(self, trade_states):
        for player_name, trade_state in trade_states.items():
            self.pick_up_developments_player(
                player_name, trade_state)

    def pick_up_developments_player(self, player_name, state):
        perspective_name = f"{player_name} view {player_name}"
        development_index = self.catan.card_lookup["Development"]
        to_pick_up = state[perspective_name][development_index]
        while to_pick_up > 0 and len(self.development_deck) > 0:
            to_pick_up = self.pick_up_development(
                perspective_name, state, to_pick_up)

    def pick_up_development(self, perspective_name, state, to_pick_up):
        card = self.development_deck.pop(0)
        state[perspective_name][self.catan.card_lookup[card]] += 1
        state[perspective_name][self.catan.card_lookup["Development"]] -= 1
        to_pick_up -= 1
        return to_pick_up

    def get_resource_trades(self, state_total):
        ranges = [np.arange(total + 1) for total in state_total]
        trades = [np.ravel(grid) for grid in np.meshgrid(*ranges)]
        trades = np.stack(trades, axis=1)
        return trades
    
    def output_states(self, states):
        string = "\n\n".join(
            self.catan.get_state_string(state)
            for state in states.values())
        return string


def trade_function_self(trade_value, perspective_value):
    return trade_value + perspective_value

def trade_function_other(trade_value, perspective_value):
    return max(0, trade_value + perspective_value)

trade_functions = {
    True : trade_function_self,
    False: trade_function_other}
