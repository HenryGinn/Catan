from numpy import array, zeros

from Players.player import Player
from Players.player_perspective import PlayerPerspective

from global_variables import initial_state


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
        for perspective in self.perspectives:
            perspective.card_state = initial_state.copy()

    def set_initial_geometry_state(self):
        self.geometry_state = {
            "Settlements": zeros(len(self.catan.board.vertices)).astype("int8"),
            "Cities": zeros(len(self.catan.board.vertices)).astype("int8"),
            "Roads": zeros(len(self.catan.board.edges)).astype("int8")}

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
            key: array(state[key])
            for key in ["Settlements", "Cities", "Roads"]}
    
    def load_perspectives_from_state(self, state):
        self.perspectives = [
            self.load_perspective_from_state(state, player.name)
            for player in self.catan.players]

    def load_perspective_from_state(self, state, perspective_view):
        view = self.catan.get_player(perspective_view)
        perspective = PlayerPerspective(view, self)
        perspective.card_state = array(state[perspective.name])
        return perspective

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
            {"Robber": tile.vector, "Players": {
                self.name: {f"Random {other_player.name}": 1},
                other_player.name: {f"Random {self.name}": -1}}}
            for tile in self.board.tiles
            for other_player in self.players
            if other_player != self]
        for i in self.knight_trades:
            print(i)

            
    # Output

    def __str__(self):
        state = self.get_state()
        string = self.catan.get_state_string(state)
        return string
