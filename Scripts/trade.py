from hgutilities.utils import json
import numpy as np
import pandas as pd

from global_variables import (
    sizes,
    real_estates,
    action_columns)


class Trade():

    def __init__(self, turn, player):
        self.game = turn.game
        self.turn = turn
        self.log = turn.log
        self.player = player
        self.init_states()
        self.init_actions()

    def init_states(self):
        self.states = [
            perspective.get_initial_states()
            for perspective in self.player.perspectives]

    def init_actions(self):
        self.actions = pd.DataFrame([{
            item: np.nan for item in action_columns}])
    
    def update_states(self, index, card_type, states):
        self.states[index][card_type] = np.vstack(
            (self.states[index][card_type], states))

    def update_actions_cards(self):
        print(self.actions)

    # Each state passed into the neural network must look the same. That
    # means that for each card states being considered there must be a
    # corresponding geometry state.
    
    def stack_real_estate(self, count):
        for perspective, states in zip(self.player.perspectives, self.states):
            for real_estate in real_estates:
                states[real_estate] = np.tile(
                    perspective.base.geometry_state[real_estate], (count, 1))


    # After all player related state stuff is done.
    
    def prepare_for_evaluation(self):
        counts = self.get_counts()
        self.validate_count(counts)
        self.count = counts[0]
        self.set_meta_data()

    def get_count(self):
        counts = np.array([
            array.shape[0]
            for perspective_state in self.states
            for array in perspective_state.values])
        return counts

    def validate_counts(self, counts):
        if np.any(counts != np.mean(counts)):
            self.log.error(f"Invalid states\n{json.dumps(self.states)}")
            raise ValueError(
                "All states must be the same size")
    
    def set_meta_data(self):
        self.init_meta_data()
        self.stack_meta_data()

    def init_meta_data(self):
        self.meta_data = {
            "PlayedDevelopmentCard": self.turn.played_development_card,
            "Robber": self.game.robber_state,
            } | self.game.board.tiles_state
    
    def stack_meta_data(self):
        self.meta_data = {
            key: np.tile(value, (self.count, 1))
            for key, value in self.meta_data} 
