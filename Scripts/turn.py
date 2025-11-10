import numpy as np
from hgutilities.utils import json

from output_state import plot_card_state
from global_variables import (
    card_types,
    resource_types)


zero = np.array([0])

class Turn():

    trade_limit = 10
    
    def __init__(self, game):
        self.game = game
        self.log = self.game.log
        np.random.seed(self.game.seed)
        self.set_player()
        self.trade_count = 0
        self.played_development_card = False
        self.traded_this_cycle = True

    def set_player(self):
        self.game.move += 1
        turn = (self.game.move - 1) % 4
        self.player = self.game.players[turn]
        self.log.info(
            f"Starting move {self.game.move}. "
            f"Player {self.player.name} to move")

    def execute_dice_roll(self):
        self.set_dice_result()

    def set_dice_result(self):
        dice_1 = np.random.randint(1, 7)
        dice_2 = np.random.randint(1, 7)
        self.dice_result = dice_1 + dice_2
        self.log.info(
            f"Dice result: {self.dice_result}")

    def take_turn(self):
        while self.continue_exploring_trades():
            self.traded_this_cycle = False
            self.log.debug(f"Begining trading cycle {self.trade_count + 1}")
            self.generate_possible_trades()
            self.evaluate_trades()
            self.execute_trades()
        self.log.info(f"Turn ended after {self.trade_count} actions")

    def continue_exploring_trades(self):
        if self.trade_count > self.trade_limit:
            self.log.debug(f"Trade limit reached")
            return False
        else:
            self.log.debug(f"Trade limit unreached. {self.traded_this_cycle=}")
            return self.traded_this_cycle

    def generate_possible_trades(self):
        self.generate_trades_with_players()
        self.generate_trades_assets()
        self.generate_trades_play_development_card()

    def generate_trades_with_players(self):
        self.log.debug("Considering trades with other players")
        for other_perspective in self.player.perspectives[1:2]:
            self.other = other_perspective.them
            self.set_non_traders()
            self.log.debug(f"Considering trades with {self.other.name}")
            self.trade_with_player()

    def set_non_traders(self):
        self.non_traders = [
            player for player in self.game.players
            if (player is not self.player)
            and (player is not self.other)]

    def trade_with_player(self):
        self.set_all_cards()
        self.set_card_trades()
        self.count = len(self.player.card_trades["Sheep"])
        self.set_game_states_player()

    def set_all_cards(self):
        self.player.set_cards()
        self.other.set_cards()
        self.set_cards_total()
        self.log.debug(
            f"Total cards between {self.player.name} and {self.other.name}:\n"
            f"{json.dumps(self.cards_total)}")

    def set_cards_total(self):
        self.cards_total = {
            card_type: (
                self.player.cards[card_type] +
                self.other.cards[card_type])
            for card_type in card_types}

    def set_card_trades(self):
        card_trades = self.get_card_trades()
        self.set_card_trades_player(card_trades)
        self.set_card_trades_other()

    def get_card_trades(self):
        ranges = [
            np.arange(total + 1) if card_type in resource_types else zero
            for card_type, total in self.cards_total.items()]
        trades = [np.ravel(grid) for grid in np.meshgrid(*ranges)]
        trades = dict(zip(card_types, trades))
        return trades

    def set_card_trades_player(self, card_trades):
        self.player.card_trades = {
            card_type: (card_trades[card_type] - self.player.cards[card_type])
            for card_type in card_types}

    def set_card_trades_other(self):
        self.other.card_trades = {
            card_type: -self.player.card_trades[card_type]
            for card_type in card_types}

    def set_game_states_player(self):
        self.card_trade_view_others(self.player, self.other)
        self.card_trade_view_others(self.other, self.player)
    
    def card_trade_view_others(self, trader, other):
        trader.set_self_card_states()
        self.card_trade_view_trader(trader, other)
        self.card_trade_view_non_traders(trader)

    def card_trade_view_trader(self, trader, other):
        perspective = trader.get_perspective(other.name)
        perspective.set_states()
        
    def card_trade_view_non_traders(self, trader):
        for perspective in trader.perspectives:
            if perspective.them in self.non_traders:
                perspective.set_view_non_trader()

    def generate_trades_assets(self):
        self.log.debug("Considering buying assets")

    def generate_trades_play_development_card(self):
        if not self.played_development_card:
            self.log.debug("Considering playing a development card")
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

