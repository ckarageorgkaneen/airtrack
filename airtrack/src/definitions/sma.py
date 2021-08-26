from enum import Enum

from airtrack.data import utils

state_transitions = utils.bpodify_state_transition_table()
states = list(state_transitions.keys())
AirtrackState = Enum('AirtrackState', states)
for state in AirtrackState:
    state.transitions = state_transitions[state.name]
