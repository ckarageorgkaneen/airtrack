import logging
import functools

from state import AirtrackState as State
from pybpodapi.protocol import Bpod
from pybpodapi.protocol import StateMachine

# logging.basicConfig()
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
        is_subject_in_lane = self._subject.is_inside_lane()
        value = int(is_subject_in_lane)
        self._bpod.manual_override(
            Bpod.ChannelTypes.INPUT,
            Bpod.ChannelNames.BNC,
            channel_number=1,
            value=value)

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
                Bpod.Events.BNC1High: State.ENTER_LANE,
                Bpod.Events.BNC1Low: State.EXIT_LANE
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
