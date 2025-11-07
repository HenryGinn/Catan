import numpy as np
from hgutilities.utils import json

from output_state import plot_card_state
from global_variables import resource_types


class Turn():

    trade_limit = 10
    
    def __init__(self, catan):
        self.catan = catan
        self.set_player()
        self.trade_count = 0
        self.played_development_card = False
        self.traded_this_cycle = True

    def set_player(self):
        self.catan.moves += 1
        turn = self.catan.moves % 4
        self.player = self.catan.players[turn]

    def take_turn(self):
        while self.continue_exploring_trades():
            self.traded_this_cycle = False
            self.generate_possible_trades()
            self.evaluate_trades()
            self.execute_trades()

    def continue_exploring_trades(self):
        if self.trade_count > self.trade_limit:
            return False
        else:
            return self.traded_this_cycle

    def generate_possible_trades(self):
        self.generate_trades_with_players()
        self.generate_trades_assets()
        self.generate_trades_play_development_card()

    def generate_trades_with_players(self):
        for other_perspective in self.player.perspectives[1:2]:
            self.other = other_perspective.them
            self.set_non_traders()
            self.trade_with_player()

    def set_non_traders(self):
        self.non_traders = [
            player for player in self.catan.players
            if (player is not self.player)
            and (player is not self.other)]

    def trade_with_player(self):
        self.set_all_resources()
        self.set_card_trades()
        self.count = len(self.player.card_trades)
        self.set_game_states_player()

    def set_all_resources(self):
        self.player.set_resources()
        self.other.set_resources()
        self.set_resources_total()

    def set_resources_total(self):
        self.resources_total = {
            resource_type: (
                self.player.resources[resource_type] +
                self.other.resources[resource_type])
            for resource_type in resource_types}

    def set_card_trades(self):
        card_trades = self.get_card_trades()
        self.set_card_trades_player(card_trades)
        self.set_card_trades_other()

    def get_card_trades(self):
        ranges = [np.arange(total + 1) for total in self.resources_total.values()]
        trades = [np.ravel(grid) for grid in np.meshgrid(*ranges)]
        trades = dict(zip(resource_types, trades))
        return trades

    def set_card_trades_player(self, card_trades):
        self.player.card_trades = {
            resource_type: (card_trades[resource_type] - self.player.resources[resource_type])
            for resource_type in resource_types}

    def set_card_trades_other(self):
        self.other.card_trades = {
            resource_type: -self.player.card_trades[resource_type]
            for resource_type in resource_types}

    def set_game_states_player(self):
        self.card_trade_view_others(self.player, self.other)
        #self.card_trade_view_others(self.other, self.player)
    
    def card_trade_view_others(self, trader, other):
        #trader.set_card_states_from_card_trades_self()
        self.card_trade_view_trader(trader, other)
        #self.card_trade_view_non_traders(trader)

    # Trader is making a trade with other. Trader does not know the card
    # state of other. Trader knows that each proposed trade is doable
    # by other. It is an implementation detail that trader knows all
    # possible trades that other can make and can thus deduce their deck. In
    # reality a player can only get answers on whether another player would
    # make a trade, not whether they can. Because of this, each trade must
    # be considered in isolation where the only knowledge the trader can
    # deduce is that the trade being considered is possible for the other
    # player to execute. This places bounds on the number of cards of
    # each type which is the posterior information provided.
    # P(k given they have lost m cards) =
    #   P(K - m) / (P(m) + ... + P(19)) if k < 19 - m, 0 otherwise
    def card_trade_view_trader(self, trader, other):
        perspective = trader.get_perspective(other.name)
        for resource_type in resource_types:
            perspective.update_distribution(resource_type)

    def card_trade_view_non_traders(self, trader):
        for perspective in trader.perspectives:
            if perspective.them in self.non_traders:
                perspective.card_states = np.tile(
                    perspective.card_state, (self.count, 1))

    def generate_trades_assets(self):
        pass

    def generate_trades_play_development_card(self):
        if not self.played_development_card:
            self.do_generate_trades_play_development_card()

    def do_generate_trades_play_development_card(self):
        pass



    # Evaluating and executing trades

    def evaluate_trades(self):
        pass

    def execute_trades(self):
        pass


    # Manually trading.
    # Converting a human-readable input into the machine-readable
    # description and then executing it.

    def trade_players_input(self, trade):
        pass

    def trade_assets_input(self, trade):
        pass

    def play_development_input(self, trade):
        pass

