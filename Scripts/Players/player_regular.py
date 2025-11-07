import numpy as np

from Players.player import Player
from Players.player_perspective import PlayerPerspective

from global_variables import resource_types


class PlayerRegular(Player):

    def __init__(self, catan, name, color):
        super().__init__(catan, name)
        self.color = color

    def initialise_perspectives(self):
        self_index = self.catan.players.index(self)
        indexes = [(self_index + i) % 4 for i in range(4)]
        self.perspectives = [
            PlayerPerspective(self.catan.players[index], self)
            for index in indexes]

    def set_initial_states(self):
        self.set_initial_geometry_state()

    def set_initial_geometry_state(self):
        self.geometry_state = {
            "Settlements": np.zeros(len(self.catan.board.vertices)).astype("int8"),
            "Cities": np.zeros(len(self.catan.board.vertices)).astype("int8"),
            "Roads": np.zeros(len(self.catan.board.edges)).astype("int8")}

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


    def set_resources(self):
        self.set_cards()
        self.resources = {
            card_type: self.cards[card_type]
            for card_type in resource_types}

    def set_cards(self):
        card_state = self.perspectives[0].card_state
        self.ensure_valid_card_state(card_state)
        self.cards = {
            card_type: np.where(distribution == 1)[0]
            for card_type, distribution in card_state.items()}

    # Both these tests ensure that a player has no uncertainty in their own
    # deck. Each card should have a 1 in its distribution with all other
    # entries equal to 0. The only time a player does not have certainty in
    # their own deck is when they are considering playing a development card
    # or moving the robber and stealing from another player.
    def ensure_valid_card_state(self, card_state):
        all_card_types_have_one = self.get_all_card_types_have_one(card_state)
        total_is_eleven = self.get_total_is_eleven(card_state)
        valid_card_state = (all_card_types_have_one and total_is_eleven)
        if not valid_card_state:
            raise ValueError(
                f"Player {self.name} has uncertainty in their own deck:\n\n{card_state}")

    def get_all_card_types_have_one(self, card_state):
        all_card_types_have_one = np.all([
            np.any(distribution == 1)
            for distribution in card_state.values()])
        return all_card_types_have_one

    def get_total_is_eleven(self, card_state):
        distribution_totals = [
            np.sum(distribution)
            for distribution in card_state.values()]
        total_is_eleven = (sum(distribution_totals) == 11)
        return total_is_eleven


    def set_card_states_from_resource_trades_self(self):
        resource_states = self.get_resource_states()
        development_state = self.perspectives[0].card_state[95:]
        development_states = np.tile(
            development_state, (self.catan.turn.count, 1))
        self.perspectives[0].card_states = np.concatenate(
            (resource_states, development_states), axis=1)

    def get_resource_states(self):
        states = np.zeros((self.catan.turn.count, 5, 19))
        card_type_indexer = np.tile(np.arange(5), (self.catan.turn.count, 1))
        card_count_indexer = np.tile(np.arange(self.catan.turn.count), (5, 1)).T
        states[card_count_indexer, card_type_indexer, self.resource_trades] = 1
        resource_states = states.reshape(-1, 95)
        return resource_states

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
            for index, resource_1 in enumerate(self.catan.resources)
            for resource_2 in self.catan.resources[index+1:]]
        return harvest_different

    def get_harvest_same(self):
        harvest_same = [
            {resource: 2}
            for resource in self.catan.resources]
        return harvest_same
        
    def precompute_road_builder(self):
        self.road_builder_trades = [
            {self.name: {"Roads": [edge_1.get_midpoint(), edge_2.get_midpoint()]}}
            for index, edge_1 in enumerate(self.catan.board.edges)
            for edge_2 in self.catan.board.edges[index+1:]]

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
        string = self.catan.get_state_string(state)
        return string
