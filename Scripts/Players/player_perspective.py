import numpy as np
from hgutilities.utils import json

from Players.player import Player
from Players.state_utils import get_updated_state
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
    
    def set_states(self):
        for card_type in card_types:
            self.states[card_type] = get_updated_state(
                card_type, self.card_state[card_type],
                self.base.card_trades[card_type])

    def set_states_non_trader(self):
        self.states = {
            card_type: np.tile(
                self.card_state[card_type],
                (self.game.turn.count, 1))
            for card_type in card_types}

    def __str__(self):
        df = self.game.get_perspective_df(self.name, self.card_state)
        string = df.to_string()
        return string
