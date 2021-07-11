import logging
import functools

from state import AirtrackState as State
from pybpodapi.protocol import Bpod
from pybpodapi.protocol import StateMachine

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

CALLBACK_MAP = {}


class AirtrackStateMachineError(Exception):
    """AirtrackStateMachine error"""


def err(message):
    logger.debug(message)
    raise AirtrackStateMachineError(message)


def callback(state):
    def decorator(func):
        CALLBACK_MAP[state] = func

        def wrapper(self):
            return func(self)
        return wrapper
    return decorator


class AirtrackStateMachine:
    def __init__(self, bpod, subject, actuator):
        self._bpod = bpod
        self._sma = StateMachine(self._bpod)
        self._subject = subject
        self._actuator = actuator
        self.callbacks = {
            s: functools.partial(f, self)
            for s, f in CALLBACK_MAP.items()
        }

    def __call__(self):
        return self._sma

    @callback(State.RESET_SUBJECT_LOCATION)
    def _reset_subject_location(self):
        if self._subject.is_inside_lane():
            event = Bpod.Events.Serial1_1
        else:
            event = Bpod.Events.Serial1_2
        self._bpod.trigger_event_by_name(event, 255)

    @callback(State.ENTER_LANE)
    def _enter_lane(self):
        print('Entered lane.')

    @callback(State.EXIT_LANE)
    def _exit_lane(self):
        print('Exited lane.')

    def setup(self):
        self._sma.add_state(
            State.INITIATE,
            state_timer=0.1,
            callback=self.callbacks.get(State.INITIATE),
            state_change_conditions={
                Bpod.Events.Tup: State.RESET_SUBJECT_LOCATION,
            })
        self._sma.add_state(
            state_name=State.RESET_SUBJECT_LOCATION,
            state_timer=0.1,
            callback=self.callbacks.get(State.RESET_SUBJECT_LOCATION),
            state_change_conditions={
                Bpod.Events.Serial1_1: State.ENTER_LANE,
                Bpod.Events.Serial1_2: State.EXIT_LANE
            })
        self._sma.add_state(
            state_name=State.ENTER_LANE,
            state_timer=0.1,
            callback=self.callbacks.get(State.ENTER_LANE),
            state_change_conditions={
                Bpod.Events.Tup: State.RESET_SUBJECT_LOCATION},
            output_actions=[
                (Bpod.OutputChannels.BNC1, 255),
                (Bpod.OutputChannels.BNC2, 0),
            ])
        self._sma.add_state(
            state_name=State.EXIT_LANE,
            state_timer=0.1,
            callback=self.callbacks.get(State.EXIT_LANE),
            state_change_conditions={
                Bpod.Events.Tup: State.RESET_SUBJECT_LOCATION},
            output_actions=[
                (Bpod.OutputChannels.BNC1, 0),
                (Bpod.OutputChannels.BNC2, 255),
            ])
