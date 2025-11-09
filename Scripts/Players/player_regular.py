import numpy as np

from Players.player import Player
from Players.player_perspective import PlayerPerspective

from global_variables import (
    card_types,
    arange_lookup)


class PlayerRegular(Player):

    def __init__(self, game, name, color):
        super().__init__(game, name)
        self.color = color

    def initialise_perspectives(self):
        self_index = self.game.players.index(self)
        indexes = [(self_index + i) % 4 for i in range(4)]
        self.perspectives = [
            PlayerPerspective(self.game.players[index], self)
            for index in indexes]

    def set_initial_states(self):
        self.set_initial_geometry_state()

    def set_initial_geometry_state(self):
        self.geometry_state = {
            "Settlements": np.zeros(len(self.game.board.vertices)).astype("int8"),
            "Cities": np.zeros(len(self.game.board.vertices)).astype("int8"),
            "Roads": np.zeros(len(self.game.board.edges)).astype("int8")}

    def get_state(self):
        perspective_states = self.get_perspective_states()
        state = {**self.geometry_state,
                 **perspective_states}
        return state

    def get_perspective_states(self):
        perspective_states = {
            perspective.name: perspective.card_state
            for perspective in self.perspectives}
        return perspective_states

    def update_state(self, state):
        self.load_geometry_from_state(state)
        self.load_perspectives_from_state(state)

    def load_geometry_from_state(self, state):
        self.geometry_state = {
            key: np.array(state[key])
            for key in ["Settlements", "Cities", "Roads"]}
    
    def load_perspectives_from_state(self, state):
        for perspective in self.perspectives:
            perspective.card_state = {
                card_type: np.array(distribution)
                for card_type, distribution in state[perspective.name].items()}

    def get_perspective_state(self, player_name):
        perspective = [
            persective for perspective in self.perspectives
            if perspective.name == player_name][0]
        return perspective.card_state

    def get_perspective(self, perspective_name):
        perspective = [
            perspective for perspective in self.perspectives
            if perspective.view == perspective_name][0]
        return perspective


    def set_cards(self):
        card_state = self.perspectives[0].card_state
        self.ensure_valid_card_state(card_state)
        self.cards = {
            card_type: int(np.where(distribution == 1)[0])
            for card_type, distribution in card_state.items()}

    # Both these tests ensure that a player has no uncertainty in their own
    # deck. Each card should have a 1 in its distribution with all other
    # entries equal to 0. The only time a player does not have certainty in
    # their own deck is when they are considering playing a development card
    # or moving the robber and stealing from another player.
    def ensure_valid_card_state(self, card_state):
        all_card_types_have_one = self.get_all_card_types_have_one(card_state)
        total_is_correct = self.get_total_is_correct(card_state)
        valid_card_state = (all_card_types_have_one and total_is_correct)
        if not valid_card_state:
            raise ValueError(
                f"Player {self.name} has uncertainty in their own deck:\n\n{card_state}")

    def get_all_card_types_have_one(self, card_state):
        all_card_types_have_one = np.all([
            np.any(distribution == 1)
            for distribution in card_state.values()])
        return all_card_types_have_one

    def get_total_is_correct(self, card_state):
        distribution_totals = [
            np.sum(distribution)
            for distribution in card_state.values()]
        total_is_correct = (sum(distribution_totals) == 11)
        return total_is_correct


    def set_self_card_states(self):
        for card_type in card_types:
            if np.all(self.card_trades[card_type] == 0):
                self.perspectives[0].set_self_states_no_change(card_type)
            else:
                self.perspectives[0].set_self_states_change(card_type)

    def set_game_states_perspectives_of_self(self):
        print("Implement me!")
        for perspective in self.perspectives[1:]:
            pass

    def update_development_trades(self):
        self.precompute_harvest()
        self.precompute_road_builder()
        self.precompute_knights()
        
    def precompute_harvest(self):
        harvest_different = self.get_harvest_different()
        harvest_same = self.get_harvest_same()
        self.harvest_trades = harvest_different + harvest_same

    def get_harvest_different(self):
        harvest_different = [
            {self.name: {resource_1: 1, resource_2: 1}}
            for index, resource_1 in enumerate(self.game.resources)
            for resource_2 in self.game.resources[index+1:]]
        return harvest_different

    def get_harvest_same(self):
        harvest_same = [
            {resource: 2}
            for resource in self.game.resources]
        return harvest_same
        
    def precompute_road_builder(self):
        self.road_builder_trades = [
            {self.name: {"Roads": [edge_1.get_midpoint(), edge_2.get_midpoint()]}}
            for index, edge_1 in enumerate(self.game.board.edges)
            for edge_2 in self.game.board.edges[index+1:]]

    def precompute_knights(self):
        self.knight_trades = [
            {"Robber": np.tile.vector, "Players": {
                self.name: {f"Random {other_player.name}": 1},
                other_player.name: {f"Random {self.name}": -1}}}
            for np.tile in self.board.np.tiles
            for other_player in self.players
            if other_player != self]
        for i in self.knight_trades:
            print(i)

            
    # Output

    def __str__(self):
        state = self.get_state()
        string = self.game.get_state_string(state)
        return string
