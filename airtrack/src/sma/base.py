import logging
import functools

from airtrack.src.actuator.base import AirtrackActuator
from airtrack.src.subject.base import AirtrackSubject
from airtrack.src.definitions.sma import AirtrackState as State

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


class AirtrackStateMachine(StateMachine):
    DEFAULT_INIT_STATE_TIMER = 3
    DEFAULT_TRANSITION_TIMER = 0.1

    def __init__(self, bpod):
        super().__init__(bpod)
        self._bpod = bpod
        self._subject = AirtrackSubject()
        self._actuator = AirtrackActuator(self._bpod)
        self.callbacks = {
            s: functools.partial(f, self)
            for s, f in CALLBACK_MAP.items()
        }

    @callback(State.QUERY_SUBJECT_LOCATION)
    def _query_subject_location(self):
        if self._subject.is_inside_lane():
            event = Bpod.Events.Serial1_1
        else:
            event = Bpod.Events.Serial1_2
        self._bpod.trigger_event_by_name(event, 255)

    @callback(State.ENTER_LANE)
    def _enter_lane(self):
        self._actuator.peek(push_timeout=3, at_rest_timeout=3)

    @callback(State.EXIT_LANE)
    def _exit_lane(self):
        self._actuator.pull()

    def setup(self):
        self.add_state(
            State.INITIATE,
            state_timer=self.DEFAULT_INIT_STATE_TIMER,
            callback=self.callbacks.get(State.INITIATE),
            state_change_conditions={
                Bpod.Events.Tup: State.QUERY_SUBJECT_LOCATION,
            })
        self.add_state(
            state_name=State.QUERY_SUBJECT_LOCATION,
            state_timer=self.DEFAULT_TRANSITION_TIMER,
            callback=self.callbacks.get(State.QUERY_SUBJECT_LOCATION),
            state_change_conditions={
                Bpod.Events.Serial1_1: State.ENTER_LANE,
                Bpod.Events.Serial1_2: State.EXIT_LANE
            })
        self.add_state(
            state_name=State.ENTER_LANE,
            state_timer=self.DEFAULT_TRANSITION_TIMER,
            callback=self.callbacks.get(State.ENTER_LANE),
            state_change_conditions={
                Bpod.Events.Tup: State.QUERY_SUBJECT_LOCATION})
        self.add_state(
            state_name=State.EXIT_LANE,
            state_timer=self.DEFAULT_TRANSITION_TIMER,
            callback=self.callbacks.get(State.EXIT_LANE),
            state_change_conditions={
                Bpod.Events.Tup: State.QUERY_SUBJECT_LOCATION})

    def clean_up(self):
        self._subject.clean_up()
        self._actuator.reset()