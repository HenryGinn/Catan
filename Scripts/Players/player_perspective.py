import warnings

import numpy as np

from Players.player import Player
from global_variables import initial_state


update_tools = {
    "Sheep":            (np.zeros(19 * 3), np.arange(19), np.arange(19 * 1, 19 * 2)),
    "Ore":              (np.zeros(19 * 3), np.arange(19), np.arange(19 * 1, 19 * 2)),
    "Mud":              (np.zeros(19 * 3), np.arange(19), np.arange(19 * 1, 19 * 2)),
    "Wood":             (np.zeros(19 * 3), np.arange(19), np.arange(19 * 1, 19 * 2)),
    "Wheat":            (np.zeros(19 * 3), np.arange(19), np.arange(19 * 1, 19 * 2)),
    "Road Builder":     (np.zeros( 3 * 3), np.arange( 3), np.arange( 3 * 1,  3 * 2)),
    "Year of Plenty":   (np.zeros( 3 * 3), np.arange( 3), np.arange( 3 * 1,  3 * 2)),
    "Monopoly":         (np.zeros( 3 * 3), np.arange( 3), np.arange( 3 * 1,  3 * 2)),
    "Victory":          (np.zeros( 6 * 3), np.arange( 6), np.arange( 6 * 1,  6 * 2)),
    "Unplayed Knight":  (np.zeros(11 * 3), np.arange(11), np.arange(11 * 1, 11 * 2)),
    "Played Knight":    (np.zeros(11 * 3), np.arange(11), np.arange(11 * 1, 11 * 2))}


# Assumed distributions when states are not normalisable. These should
# not be used and are only included so that the game can continue.
guessed_distributions = {
    "Sheep":            np.array([0.303, 0.251, 0.201, 0.101, 0.030, 0.024, 0.019, 0.015, 0.012, 0.010, 0.008, 0.006, 0.005, 0.004, 0.003, 0.003, 0.002, 0.002, 0.001]),
    "Ore":              np.array([0.303, 0.251, 0.201, 0.101, 0.030, 0.024, 0.019, 0.015, 0.012, 0.010, 0.008, 0.006, 0.005, 0.004, 0.003, 0.003, 0.002, 0.002, 0.001]),
    "Mud":              np.array([0.303, 0.251, 0.201, 0.101, 0.030, 0.024, 0.019, 0.015, 0.012, 0.010, 0.008, 0.006, 0.005, 0.004, 0.003, 0.003, 0.002, 0.002, 0.001]),
    "Wood":             np.array([0.303, 0.251, 0.201, 0.101, 0.030, 0.024, 0.019, 0.015, 0.012, 0.010, 0.008, 0.006, 0.005, 0.004, 0.003, 0.003, 0.002, 0.002, 0.001]),
    "Wheat":            np.array([0.303, 0.251, 0.201, 0.101, 0.030, 0.024, 0.019, 0.015, 0.012, 0.010, 0.008, 0.006, 0.005, 0.004, 0.003, 0.003, 0.002, 0.002, 0.001]),
    "Road Builder":     np.array([0.989, 0.010, 0.001]),
    "Year of Plenty":   np.array([0.989, 0.010, 0.001]),
    "Monopoly":         np.array([0.989, 0.010, 0.001]),
    "Victory":          np.array([0.568, 0.227, 0.114, 0.057, 0.023, 0.011]),
    "Unplayed Knight":  np.array([0.530, 0.396, 0.066, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]),
    "Played Knight":    np.array([0.530, 0.396, 0.066, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001])}


class PlayerPerspective(Player):

    def __init__(self, perspective, base):
        name = f"{base.name} view {perspective.name}"
        self.view = f"{perspective.name}"
        super().__init__(base.catan, name)
        self.base = base
        self.them = perspective
        self.card_state = initial_state.copy()
        self.states = {}

    def update_distribution(self, card_type):
        zeros, _, middle = update_tools[card_type]
        expanded_state = zeros.copy()
        expanded_state[middle] = self.card_state[card_type]
        indexer = middle - self.them.card_trades[card_type].reshape(-1, 1)
        self.states[card_type] = expanded_state[indexer]
        self.normalise_states(card_type)

    # There is a potential for an infinite loop here.
    # The strategy is that if a state is non-normalisable we replace it with 
    def normalise_states(self, card_type):
        denominators = np.sum(self.states[card_type], axis=1)
        invalid_states = (denominators == 0)
        if np.any(invalid_states):
            self.correct_unnormalisable_states(invalid_states, card_type)
            # The distributions that have replaced the invalid ones are normalised.
            denominators = np.where(invalid_states, 1, denominators)
        self.execute_normalise_states(denominators, card_type)

    def execute_normalise_states(self, denominators, card_type):
        self.states[card_type] = (
            self.states[card_type] / denominators.reshape(*denominators.shape, 1))


    # If there is an input error or a bug then it may be the case that
    # someone deduces someone cannot have n cards when they can. The error
    # could then propogate to the point where every card possibility is
    # ruled out, meaning the probability distribution is 0 and cannot be
    # normalised. This method flags this as a warning and reinitialises the
    # state assuming some prior distriution. This could be made a lot
    # better, for example taking the current trade information into account
    # or by the number of cards they have, but given that this should never
    # occur not much effort has been spent on it.
    def correct_unnormalisable_states(self, invalid_states, card_type):
        self.raise_warning_zero_distribution(card_type)
        distribution = guessed_distributions[card_type].copy()
        self.states[card_type][invalid_states, :] = distribution

    def raise_warning_zero_distribution(self, card_type):
        warnings.warn(
            "\nA probability distribution has collapsed and cannot be normalised.\n"
            f"{self.base.name} believes the requested change in state to {card_type} "
            f"to be incompatible with what cards {self.them.name} could hold.")

    def __str__(self):
        df = self.catan.get_perspective_df(self.name, self.card_state)
        string = df.to_string()
        return string
