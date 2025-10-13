import numpy as np


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
            self.trade_with_player(other_perspective.them)

    def trade_with_player(self, other_player):
        resources_self = self.get_resources(self.player)
        resources_other = self.get_resources(other_player)
        resources_total = resources_self + resources_other
        trades = self.get_resource_trades(resources_total)
        game_state_self = self.get_game_state(self.player, other_player, resources_total, resources_self)
        game_state_other = self.get_game_state(other_player, self.player, resources_total, resources_other)

    def get_resources(self, player):
        resources = player.perspectives[0].card_state[:95].reshape(5, 19)
        self.ensure_valid_resources(resources, player.name)
        positions, resource_type_indexes = np.where(resources == 1)
        resources = positions[resource_type_indexes]
        return resources

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

    def get_resource_trades(self, resources_total):
        ranges = [np.arange(total + 1) for total in resources_total]
        trades = [np.ravel(grid) for grid in np.meshgrid(*ranges)]
        trades = np.stack(trades, axis=1)
        return trades

    def get_game_state(self, player_self, player_other, total, resources):
        print(player_self)
        print(player_other)
        print(total)
        print(resources)


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

