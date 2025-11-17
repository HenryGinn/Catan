from hgutilities.utils import json
import numpy as np
import pandas as pd

from Players.player import Player
from Players.state_utils import (
    get_self_states,
    get_updated_states)
from global_variables import (
    initial_state,
    card_types)


class PlayerPerspective(Player):

    def __init__(self, perspective, base):
        name = f"{base.name} view {perspective.name}"
        self.view = f"{perspective.name}"
        super().__init__(base.game, name)
        self.base = base
        self.them = perspective
        self.card_state = initial_state.copy()
        self.states = {}

    def update_state(self, card_type, change):
        change = np.array(change, "int8")
        if self.base is self.them:
            self.update_state_self(card_type, change)
        else:
            self.update_state_other(card_type, change)

    def update_state_self(self, card_type, change):
        state = self.card_state[card_type]
        self.card_state[card_type] = (
            get_self_states(card_type, state, change))

    def update_state_other(self, card_type, change):
        state = self.card_state[card_type]
        self.card_state[card_type] = (
            get_updated_states(card_type, state, change))

    def update_states(self, card_type, actor_changes, count):
        if self.them in actor_changes:
            self.update_states_change(card_type, actor_changes[self.them])
        else:
            self.update_states_stack(card_type, count)

    def update_states_change(self, card_type, changes):
        if self.base is self.them:
            self.update_states_self(card_type, changes)
        else:
            self.update_states_other(card_type, changes)

    def update_states_self(self, card_type, change):
        state = self.card_state[card_type]
        self.states[card_type] = (
            get_self_states(card_type, state, change))

    def update_states_other(self, card_type, change):
        state = self.card_state[card_type]
        self.states[card_type] = (
            get_updated_states(card_type, state, change))

    def update_states_stack(self, card_type, count):
        state = self.card_state[card_type]
        self.states[card_type] = np.tile(
            state, (count, 1))
    
    def get_df(self):
        df = {
            (card_type, count): card_count_probability
            for card_type, card_distribution in self.card_state.items()
            for count, card_count_probability in enumerate(card_distribution)}
        df = pd.DataFrame({self.them.name: df})
        df.index = df.index.set_names(("Card Type", "Count"))
        return df
