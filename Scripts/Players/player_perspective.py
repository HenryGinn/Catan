import numpy as np
from hgutilities.utils import json

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

    def update_states_self(self, card_type, change):
        state = self.card_state[card_type]
        self.states[card_type] = (
            get_self_states(card_type, state, change))

    def update_states_other(self, actor, card_type, change):
        state = self.card_state[card_type]
        self.states[card_type] = (
            get_updated_states(card_type, state, change))
    
    def __str__(self):
        df = self.game.get_perspective_df(self.name, self.card_state)
        string = df.to_string()
        return string
