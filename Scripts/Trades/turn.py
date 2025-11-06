import numpy as np

from output_state import plot_card_state


zeros = np.zeros((5, 19))
resource_state_indexer = np.tile(np.arange(5), (19, 1)).T
initial_indexer = np.tile(np.arange(57), (5, 1))

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
        self.player.resource_trades = self.get_resource_trades() - self.player.resources
        self.other.resource_trades = -self.player.resource_trades
        self.count = len(self.player.resource_trades)
        self.set_game_states_player()

    def set_all_resources(self):
        self.set_resources(self.player)
        self.set_resources(self.other)
        self.resources_total = self.player.resources + self.other.resources

    def set_resources(self, player):
        resources = player.perspectives[0].card_state[:95].reshape(5, 19)
        self.ensure_valid_resources(resources, player.name)
        positions, resource_type_indexes = np.where(resources == 1)
        player.resources = positions[resource_type_indexes]

    # Both these tests ensure that a player has no uncertainty in their own
    # deck. Each card should have a 1 in its distribution with all other
    # entries equal to 0. The only time a player does not have certainty in
    # their own deck is when they are considering playing a development card
    # or moving the robber and stealing from another player.
    def ensure_valid_resources(self, resources, name):
        all_rows_have_one = np.all(np.any(resources == 1, axis=1), axis=0)
        total_is_five = np.sum(resources) == 5
        valid_resources = (all_rows_have_one and total_is_five)
        if not valid_resources:
            raise ValueError(
                f"Player {name} has uncertainty in their own deck:\n\n{resources}")

    def get_resource_trades(self):
        ranges = [np.arange(total + 1) for total in self.resources_total]
        trades = [np.ravel(grid) for grid in np.meshgrid(*ranges)]
        trades = np.stack(trades, axis=1)
        return trades

    def set_game_states_player(self):
        #self.resource_trade_view_others(self.player, self.other)
        self.resource_trade_view_others(self.other, self.player)

    def resource_trade_view_others(self, trader, other):
        trader.set_card_states_from_resource_trades_self()
        self.resource_trade_view_trader(trader, other)
        self.resource_trade_view_non_traders(trader)

    # Trader is making a trade with other. Trader does not know the card
    # state of other. Trader knows that each proposed trade is doable
    # by other. It is an implementation detail that trader knows all
    # possible trades that other can make and can thus deduce their deck. In
    # reality a player can only get answers on whether another player would
    # make a trade, not whether they can. Because of this, each trade must
    # be considered in isolation where the only knowledge the trader can
    # deduce is that the trade beinng considered is possible for the other
    # player to execute. This places a lower bound on the number of cards of
    # each type which is the posterior information provided.
    # P(k given they have lost m cards) =
    #   P(K - m) / (P(m) + ... + P(19)) if k < 19 - m, 0 otherwise
    def resource_trade_view_trader(self, trader, other):
        perspective = trader.get_perspective(other.name)
        resource_state = perspective.card_state[:95].reshape(5, 19)
        expanded_state = np.concatenate((zeros, resource_state, zeros), axis=1)
        indexer = initial_indexer - other.resource_trades.reshape(-1, 5, 1)
        indexer = indexer[:, :, 19:38]
        perspective.states = expanded_state[resource_state_indexer, indexer]
        perspective.normalise_states()
        
    def resource_trade_view_non_traders(self, trader):
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

