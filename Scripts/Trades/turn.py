import numpy as np

from output_state import plot_card_state


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
            self.trade_with_players()
            self.trade_assets()
            self.trade_play_development_card()

    def continue_exploring_trades(self):
        if self.trade_count > self.trade_limit:
            return False
        else:
            return self.traded_this_cycle

    def trade_with_players(self):
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
        self.player.resource_trades = self.get_resource_trades()
        self.other.resource_trades = self.resources_total - self.player.resource_trades
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
        #self.player.set_card_states_from_resource_trades_self()
        #self.other.set_card_states_from_resource_trades_self()
        self.set_game_states_non_trading_players()

    def get_resource_states(self, resources):
        states = np.zeros((self.count, 5, 19))
        card_type_indexer = np.tile(np.arange(5), (self.count, 1))
        card_count_indexer = np.tile(np.arange(self.count), (5, 1)).T
        states[card_count_indexer, card_type_indexer, resources] = 1
        return states

    def set_game_states_non_trading_players(self):
        for player in self.non_traders[:1]:                     ###### REMEMBER TO RESET THIS
            self.set_game_states_non_trading_player(player)

    def set_game_states_non_trading_player(self, player):
        #self.set_game_states_non_trading_player_non_traders(player)
        self.set_game_states_other_trader_perspective(player, self.player)
        #self.set_game_states_other_trader_perspective(player, self.other)

    def set_game_states_non_trading_player_non_traders(self, player):
        for perspective in player.perspectives:
            if perspective.them in self.non_traders:
                perspective.card_states = np.tile(
                    perspective.card_state, (self.count, 1))

    # Trader is the one making the trades.
    # Player is any other player.
    # Other knows what trades are being made, but not the traders card state.
    def set_game_states_other_trader_perspective(self, player, trader):
        perspective = player.get_perspective(trader.name)
        resource_state = perspective.card_state[:95].reshape(5, 19)
        print(resource_state)
        print(trader.resource_trades)
        

    def trade_assets(self):
        pass

    def trade_play_development_card(self):
        if not self.played_development_card:
            self.do_trade_play_development_card()

    def do_trade_play_development_card(self):
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

