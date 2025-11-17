"""
The number of cards that Player has is changing. Other does not know the
card state of Player. Other knows that each proposed change is doable by
Player. When trading it is a consequence of implementation that Other
knows all possible trades that Player can make and can thus deduce their
deck. In reality a player can only get answers on whether another player
would make a trade, not whether they can. Because of this, each change
in card state must be considered in isolation where the only knowledge
that Other can deduce is that the change being considered is possible
for Player. This places bounds on the number of cards of each type which
is the posterior information provided. P(k given they have lost m cards)
= P(K - m) / (P(m) + ... + P(19)) if k < 19 - m, 0 otherwise.
  
If no cards of a given card type are exchanged in any of the trades then
it is cheaper to simply stack the current state. This is
especially the case for development cards which will always pass this
test for resource card trades.

change can either be a scalar or a 1d numpy array.
"""


import logging
log = logging.getLogger("game")

import numpy as np

from global_variables import sizes


# Assumed states when states are not normalisable. These should
# not be used and are only included so that the game can continue.
guessed_states = {
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

zeros_lookup = {
    card_type: np.zeros(size * 3)
    for card_type, size in sizes.items()}

middle_lookup = {
    card_type: np.arange(size, size * 2)
    for card_type, size in sizes.items()}

arange_lookup = {
    card_type: np.arange(size)
    for card_type, size in sizes.items()}


def get_updated_states(card_type, state, change):
    state = get_updated_state_split_on_change(
        card_type, state, change)
    state = np.squeeze(state)
    return state

def get_updated_state_split_on_change(card_type, state, change):
    if np.all(change == 0):
        state = get_updated_state_no_change(card_type, state, change)
    else:
        state = get_updated_state_change(card_type, state, change)
    return state

def get_updated_state_no_change(card_type, state, change):
    state = np.tile(
        state, (change.size, 1))
    return state

def get_updated_state_change(card_type, state, change):
    state = get_changeed_state(card_type, state, change)
    state = get_normalised_state(card_type, state)
    state = state.round(6)
    return state

def get_changeed_state(card_type, state, change):
    zeros = zeros_lookup[card_type]
    middle = middle_lookup[card_type]
    expanded_state = zeros.copy()
    expanded_state[middle] = state
    indexer = middle - change.reshape(-1, 1)
    state = expanded_state[indexer]
    return state

def get_normalised_state(card_type, state):
    denominators = np.sum(state, axis=1)
    invalid_states = (denominators == 0)
    if np.any(invalid_states):
        state = correct_unnormalisable_states(state, invalid_states, card_type)
        # The states that have replaced the invalid ones are normalised.
        denominators = np.where(invalid_states, 1, denominators)
    state = execute_normalise_state(state, denominators, card_type)
    return state

def execute_normalise_state(state, denominators, card_type):
    state = (
        state / denominators.reshape(*denominators.shape, 1))
    return state

# If there is an input error or a bug then it may be the case that
# someone deduces someone cannot have n cards when they can. The error
# could then propogate to the point where every card possibility is
# ruled out, meaning the probability state is 0 and cannot be
# normalised. This method flags this as a warning and reinitialises the
# state assuming some prior distriution. This could be made a lot
# better, for example taking the current trade information into account
# or by the number of cards they have, but given that this should never
# occur not much effort has been spent on it.
def correct_unnormalisable_states(state, invalid_states, card_type):
    raise_warning_zero_state(card_type)
    state[invalid_states, :] = guessed_states[card_type].copy()
    return state

def raise_warning_zero_state(card_type):
    log.warning(
        "A probability distribution has collapsed and cannot be normalised.\n"
        f"The requested change in state to {card_type} is believed to be "
        "incompatible with what cards the other player could hold.")


def get_self_states(card_type, state, change):
    state = get_self_state_split_on_change(card_type, state, change)
    state = np.squeeze(state)
    return state

def get_self_state_split_on_change(card_type, state, change):
    if np.all(change == 0):
        state = get_self_states_no_change(card_type, state, change)
    else:
        state = get_self_states_change(card_type, state, change)
    return state

def get_self_states_no_change(card_type, state, change):
    state = np.tile(state, (change.size, 1))
    return state

def get_self_states_change(card_type, state, change):
    card_count = int(np.where(state == 1)[0])
    indexes = card_count + change
    state = np.zeros((change.size, sizes[card_type]))
    state[np.arange(change.size), indexes] = 1
    return state
