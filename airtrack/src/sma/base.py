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
import logging
import functools

from airtrack.src.actuator import AirtrackActuator
from airtrack.src.subject import AirtrackSubject
from airtrack.src.definitions import AirtrackState as State
from airtrack.src.errors import on_error_raise
from airtrack.src.errors import AirtrackStateMachineError

from pybpodapi.protocol import Bpod
from pybpodapi.protocol import StateMachine

logger = logging.getLogger(__name__)

handle_error = on_error_raise(AirtrackStateMachineError, logger)


def callback(state):
    def decorator(func):
        def wrapper(self):
            logger.debug(f"@@@@@@@@@>>>> Calling {state} callback")
            return func(self)
        state.callback = wrapper
        return wrapper
    return decorator


class AirtrackStateMachine(StateMachine):
    """Airtrack state machine interface."""
    DEFAULT_INIT_STATE_TIMER = 3
    DEFAULT_TRANSITION_TIMER = 0.1

    def __init__(self, bpod):
        super().__init__(bpod)
        self._bpod = bpod
        self._subject = AirtrackSubject()
        self._actuator = AirtrackActuator(self._bpod)
        # Prepare state callbacks
        for s in State:
            if hasattr(s, 'callback'):
                s.callback = functools.partial(s.callback, self)
            else:
                s.callback = None

    @callback(State.QUERY_SUBJECT_LOCATION)
    @handle_error
    def _query_subject_location(self):
        self._trigger_event_by_name(Bpod.Events.Serial1_1
                                    if self._subject.is_inside_lane() else
                                    Bpod.Events.Serial1_2)

    @callback(State.ENTER_LANE)
    @handle_error
    def _enter_lane(self):
        self._actuator.peek()

    @callback(State.EXIT_LANE)
    @handle_error
    def _exit_lane(self):
        self._actuator.pull()

    @handle_error
    def _trigger_event_by_name(self, event_name):
        self._bpod.trigger_event_by_name(event_name, 255)

    @handle_error
    def setup(self):
        """Set up the state machine."""
        self.add_state(
            State.INITIATE,
            state_timer=self.DEFAULT_INIT_STATE_TIMER,
            callback=State.INITIATE.callback,
            state_change_conditions={
                Bpod.Events.Tup: State.QUERY_SUBJECT_LOCATION,
            })
        self.add_state(
            state_name=State.QUERY_SUBJECT_LOCATION,
            state_timer=self.DEFAULT_TRANSITION_TIMER,
            callback=State.QUERY_SUBJECT_LOCATION.callback,
            state_change_conditions={
                Bpod.Events.Serial1_1: State.ENTER_LANE,
                Bpod.Events.Serial1_2: State.EXIT_LANE
            })
        self.add_state(
            state_name=State.ENTER_LANE,
            state_timer=self.DEFAULT_TRANSITION_TIMER,
            callback=State.ENTER_LANE.callback,
            state_change_conditions={
                Bpod.Events.Tup: State.QUERY_SUBJECT_LOCATION})
        self.add_state(
            state_name=State.EXIT_LANE,
            state_timer=self.DEFAULT_TRANSITION_TIMER,
            callback=State.EXIT_LANE.callback,
            state_change_conditions={
                Bpod.Events.Tup: State.QUERY_SUBJECT_LOCATION})

    @handle_error
    def clean_up(self):
        """Clean up the state machine."""
        self._subject.clean_up()
        self._actuator.reset()
