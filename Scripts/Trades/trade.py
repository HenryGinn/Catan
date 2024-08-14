import pandas as pd


class Trade():

    costs = {
        "Settlement": {"Wheat": 1,
                       "Mud": 1,
                       "Wood": 1,
                       "Sheep": 1},
        "Road": {"Mud": 1,
                 "Wood": 1},
        "City": {"Wheat": 2,
                 "Ore": 3},
        "Development": {"Wheat": 1,
                        "Sheep": 1,
                        "Ore": 1}}

    def __init__(self, catan):
        self.catan = catan

    def __call__(self, trade):
        trade_states = self.get_trade_states_from_input(trade)

    def get_trade_states_from_input(self, trade):
        self.output(trade)
        trade = self.preprocess_trade_from_input(trade)
        self.output(trade)
        trade_states = [
            self.get_trade_state_from_dict(trade, player_name)
            for player_name in trade.keys()]
        return trade_states

    def preprocess_trade_from_input(self, trade):
        for player_name, player_trade in trade.items():
            player_trade = self.add_missing_keys(player_trade)
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

    def get_trade_state_from_dict(self, trade, player_name):
        player = self.catan.get_player(player_name)
        return None
        #return trade_state

    def output(self, trade):
        print("")
        print(pd.DataFrame(trade).to_string())
