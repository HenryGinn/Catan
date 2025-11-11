import numpy as np

from Players.player import Player
from Players.player_perspective import PlayerPerspective
from Players.state_utils import get_self_state
from global_variables import card_types


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
            state = self.perspectives[0].card_state[card_type]
            shift = self.card_trades[card_type]
            self.perspectives[0].states = get_self_state(
                card_type, state, shift)
    
    def __str__(self):
        state = self.get_state()
        string = self.game.get_state_string(state)
        return string
