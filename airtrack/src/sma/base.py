"""Airtrack state machine base module.

This module provides an interface (AirtrackStateMachine) for interacting with
the state machine of the Airtrack system.

Example:

    from pybpodapi.protocol import Bpod
    from airtrack.src.sma import AirtrackStateMachine

    bpod = Bpod(emulator_mode=True)
    bpod.open()

    sma = AirtrackStateMachine(bpod)
    sma.setup()

    bpod.send_state_machine(sma, ignore_emulator=True)
    bpod.run_state_machine(sma)
"""
import functools

from airtrack.src import utils

from airtrack.src.actuator import AirtrackActuator
from airtrack.src.definitions import AirtrackState as State
from airtrack.src.errors import on_error_raise
from airtrack.src.errors import AirtrackStateMachineError

from pybpodapi.protocol import Bpod
from pybpodapi.protocol import StateMachine

logger = utils.create_logger(__name__)

handle_error = on_error_raise(AirtrackStateMachineError, logger)

UNBOUND_CALLBACK_ATTR_NAME = 'unbound_callback'


def callback(state):
    def decorator(func):
        def wrapper(self):
            logger.debug(f'Calling {state} callback')
            return func(self, state)
        setattr(state, UNBOUND_CALLBACK_ATTR_NAME, wrapper)
        return wrapper
    return decorator


class AirtrackStateMachine(StateMachine):
    """Airtrack state machine interface."""
    DEFAULT_TRANSITION_TIMER = 0.1

    def __init__(self, bpod, subject):
        super().__init__(bpod)
        self._bpod = bpod
        self._subject = subject
        self._actuator = AirtrackActuator(self._bpod)
        # Bind `self` to state callbacks
        for s in State:
            unbound_callback = getattr(s, UNBOUND_CALLBACK_ATTR_NAME, None)
            if unbound_callback:
                s.callback = functools.partial(unbound_callback, self)
            else:
                s.callback = None

    @callback(State.QUERY_SUBJECT_LOCATION)
    @handle_error
    def _query_subject_location(self, state):
        if self._subject.is_inside_lane():
            dest_state_name = State.ENTER_LANE.name
        else:
            dest_state_name = State.EXIT_LANE.name
        event = state.transitions[dest_state_name]
        self._trigger_event_by_name(event)

    @callback(State.ENTER_LANE)
    @handle_error
    def _enter_lane(self, state):
        peek_completed = self._actuator.peek()
        if peek_completed:
            event = state.transitions['exit']
            self._trigger_event_by_name(event)

    @callback(State.EXIT_LANE)
    @handle_error
    def _exit_lane(self, state):
        pull_timed_out = self._actuator.pull()
        if pull_timed_out:
            event = state.transitions['exit']
            self._trigger_event_by_name(event)

    @handle_error
    def _trigger_event_by_name(self, event_name):
        self._bpod.trigger_event_by_name(event_name, 255)

    @handle_error
    def setup(self):
        """Set up the state machine."""
        for state in State:
            state_timer = None
            state_transitions = state.transitions.items()
            if len(state_transitions) == 1:
                other_state, event = next(iter(state_transitions))
                if isinstance(event, (int, float)):
                    state_timer = event
                    bpod_event = Bpod.Events.Tup
                else:
                    bpod_event = event
                state_change_conditions = {bpod_event: other_state}
            else:
                state_change_conditions = {
                    event if isinstance(event, str)
                    else Bpod.Events.Tup: other_state
                    for other_state, event in state_transitions}
            self.add_state(
                state.name,
                state_timer=state_timer or self.DEFAULT_TRANSITION_TIMER,
                callback=state.callback,
                state_change_conditions=state_change_conditions)

    @handle_error
    def clean_up(self):
        """Clean up the state machine."""
        self._actuator.reset()
