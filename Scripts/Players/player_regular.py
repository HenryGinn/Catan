import numpy as np
import pandas as pd

from Players.player import Player
from Players.player_perspective import PlayerPerspective
from global_variables import card_types


class PlayerRegular(Player):

    def __init__(self, game, name, color):
        super().__init__(game, name)
        self.color = color

    def initialise_perspectives(self):
        self_index = self.game.players.index(self)
        self.perspective_indexes = [(self_index + i) % 4 for i in range(4)]
        self.perspectives = [
            PlayerPerspective(self.game.players[index], self)
            for index in self.perspective_indexes]

    def set_initial_states(self):
        self.set_initial_geometry_state()

    def set_initial_geometry_state(self):
        self.geometry_state = {
            "Settlements": np.zeros(len(self.game.board.vertices)).astype("int8"),
            "Cities": np.zeros(len(self.game.board.vertices)).astype("int8"),
            "Roads": np.zeros(len(self.game.board.edges)).astype("int8")}

    def get_state(self):
        perspective_states = self.get_perspective_states()
        state = {
            **self.geometry_state,
            **perspective_states}
        return state

    def get_perspective_states(self):
        perspective_states = {
            perspective.name: perspective.card_state
            for perspective in self.perspectives}
        return perspective_states

    def set_from_state(self, state):
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

    def get_resources_gained(self, tile):
        vertex_values = (
            1 * self.geometry_state["Settlements"] +
            2 * self.geometry_state["Cities"])
        resources_gained = np.sum(vertex_values * tile.vertex_indicators)
        return resources_gained

    def update_state(self, actor, card_type, change):
        self.log.debug(f"Updating state of {actor.name} for {card_type} with change {change}")
        self.perspectives[0].update_state_self(card_type, change)
        for perspective in self.perspectives[1:]:
            perspective.update_state_other(actor, card_type, change)

    def set_states_resources(self, actor):
        self.log.debug((
            f"Updating {self.name}'s states for {player.name}\n"
            f"{json.dumps(player.card_trades)}"))
        for card_type, trade in player.card_trades.items():
            player.update_states(player, card_type, trade)

    def update_states(self, actor, card_type, changes):
        self.perspectives[0].update_states_self(card_type, changes)
        for perspective in self.perspectives[1:]:
            perspective.update_states_other(actor, card_type, changes)

    def get_card_df(self):
        perspective_dfs = [
            self.perspectives[(4 - index) % 4].get_df()
            for index in self.perspective_indexes]
        card_df = pd.concat(perspective_dfs, axis=1)
        card_df.columns = pd.MultiIndex.from_product(
            [[self.name], card_df.columns.to_list()])
        return card_df
        
