import warnings

import numpy as np
from hgutilities.utils import json

from Players.player import Player
from global_variables import (
    initial_state,
    card_types,
    sizes,
    zeros_lookup,
    middle_lookup,
    guessed_distributions)


class PlayerPerspective(Player):

    def __init__(self, perspective, base):
        name = f"{base.name} view {perspective.name}"
        self.view = f"{perspective.name}"
        super().__init__(base.catan, name)
        self.base = base
        self.them = perspective
        self.card_state = initial_state.copy()
        self.states = {}

    def set_self_states_no_change(self, card_type):
        self.states[card_type] = np.tile(
            self.card_state[card_type],
            (self.catan.turn.count, 1))
    
    def set_self_states_change(self, card_type):
        indexes = self.base.cards[card_type] + self.base.card_trades[card_type]
        state = np.zeros((self.catan.turn.count, sizes[card_type]))
        state[np.arange(self.catan.turn.count), indexes] = 1
        self.states[card_type] = state
    
    # Base is making a trade with Them. Base does not know the card state of
    # Them. Base knows that each proposed trade is doable by Them. It is a
    # consequence of implementation that Base knows all possible trades that
    # Them can make and can thus deduce their deck. In reality a player can
    # only get answers on whether another player would make a trade, not
    # whether they can. Because of this, each trade must be considered in
    # isolation where the only knowledge that Base can deduce is that the
    # trade being considered is possible for Them to execute. This places
    # bounds on the number of cards of each type which is the posterior
    # information provided.
    # P(k given they have lost m cards) =
    #   P(K - m) / (P(m) + ... + P(19)) if k < 19 - m, 0 otherwise
    #
    # The if statement here is because if no cards of a given card type are
    # exchanged in any of the trades then it is cheaper to simply stack the
    # current distribution. This is especially the case for development
    # cards which will always pass this test for resource card trades.
    def set_states(self):
        for card_type in card_types:
            if np.all(self.base.card_trades[card_type] == 0):
                self.update_distribution_no_change(card_type)
            else:
                self.update_distribution_change(card_type)

    def update_distribution_no_change(self, card_type):
        self.states[card_type] = np.tile(
            self.card_state[card_type],
            (self.catan.turn.count, 1))

    def update_distribution_change(self, card_type):
        zeros = zeros_lookup[card_type]
        middle = middle_lookup[card_type]
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

    def set_view_non_trader(self):
        self.states = {
            card_type: np.tile(
                self.card_state[card_type],
                (self.catan.turn.count, 1))
            for card_type in card_types}
                        
    def __str__(self):
        df = self.catan.get_perspective_df(self.name, self.card_state)
        string = df.to_string()
        return string
