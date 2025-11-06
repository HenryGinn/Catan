import numpy as np

from Players.player import Player
from global_variables import initial_state


class PlayerPerspective(Player):

    def __init__(self, perspective, base):
        name = f"{base.name} view {perspective.name}"
        self.view = f"{perspective.name}"
        super().__init__(base.catan, name)
        self.base = base
        self.them = perspective
        self.card_state = initial_state.copy()

    def normalise_states(self):
        denominators = np.sum(self.states, axis=2)
        if np.any(denominators == 0):
            self.normalise_states_with_correction(denominators)
        else:
            self.normalise_states_regular(denominators)

    def normalise_states_regular(self, denominators):
        self.states = self.states / denominators.reshape(*denominators.shape, 1)
        self.states = np.round(self.states, 2)


    # If there is an input error or a bug then it may be the case that
    # someone deduces someone cannot have n cards when they can. The error
    # could then propogate to the point where every card possibility is
    # ruled out, meaning the probability distribution is 0 and cannot be
    # normalised. This method flags this as a warning and reinitialises the
    # state based only on the information they are told right now about what
    # is happening to the state. For example if they are told they are
    # losing two wheat then it will be assumed that after the trade they are
    # equally likely to have 0 to 16 wheat. This is not a good assumption
    # and better estimates could be given based on assuming a distribution
    # of cards and using the number of cards they hold in their deck. Given
    # this should never occur, not much effort is put into this.
    def normalise_states_with_correction(self, denominators):
        self.raise_warning_zero_distribution()
        guessed_states = self.get_guessed_states()

    def raise_warning_zero_distribution(self):
        raise Warning(
            "A probability distribution has collapsed and cannot be normalised.\n"
            f"{self.name} believes the requested change in state to be incompatible with what cards")

    def get_guessed_states(self):
        trades = self.them.resource_trades
        indexer = np.tile(np.arange(19), (*trades.shape, 1))
        state_changes = np.swapaxes(np.tile(trades, (19, 1, 1)).T, 0, 1)
        guessed_states = np.where(indexer >= state_changes, 1, 0)
        guessed_states = np.where(
            indexer <= 18 + np.minimum(0, state_changes), guessed_states, 0)
        return guessed_states

    def __str__(self):
        df = self.catan.get_perspective_df(self.name, self.card_state)
        string = df.to_string()
        return string
