import random
from state import AirtrackState as State
from pybpodapi.protocol import Bpod
from pybpodapi.protocol import StateMachine


class AirtrackStateMachine:
    def __init__(self, bpod, camera, actuator):
        self._bpod = bpod
        self._sma = StateMachine(self._bpod)
        self._camera = camera
        self._actuator = actuator
        self._callbacks = {
            State.INITIATE: None,
            State.RESET_SUBJECT_LOCATION: self._cb_reset_subject_location,
            State.ENTER_LANE: self._cb_enter_lane,
            State.EXIT_LANE: self._cb_exit_lane
        }

    def __call__(self):
        return self._sma

    def _cb_reset_subject_location(self):
        value = random.choice([1, 0])
        self._bpod.manual_override(
            Bpod.ChannelTypes.INPUT,
            Bpod.ChannelNames.BNC,
            channel_number=1,
            value=value)

    def _cb_enter_lane(self):
        print('Entered lane.')

    def _cb_exit_lane(self):
        print('Exited lane.')

    def setup(self):
        self._sma.add_state(
            State.INITIATE,
            state_timer=0.1,
            callback=self._callbacks[State.INITIATE],
            state_change_conditions={
                Bpod.Events.Tup: State.RESET_SUBJECT_LOCATION,
            })
        self._sma.add_state(
            state_name=State.RESET_SUBJECT_LOCATION,
            state_timer=0.1,
            callback=self._callbacks[State.RESET_SUBJECT_LOCATION],
            state_change_conditions={
                Bpod.Events.BNC1High: State.ENTER_LANE,
                Bpod.Events.BNC1Low: State.EXIT_LANE
            })
        self._sma.add_state(
            state_name=State.ENTER_LANE,
            state_timer=0.1,
            callback=self._callbacks[State.ENTER_LANE],
            state_change_conditions={
                Bpod.Events.Tup: State.RESET_SUBJECT_LOCATION},
            output_actions=[
                (Bpod.OutputChannels.BNC1, 255),
                (Bpod.OutputChannels.BNC2, 0),
            ])
        self._sma.add_state(
            state_name=State.EXIT_LANE,
            state_timer=0.1,
            callback=self._callbacks[State.EXIT_LANE],
            state_change_conditions={
                Bpod.Events.Tup: State.RESET_SUBJECT_LOCATION},
            output_actions=[
                (Bpod.OutputChannels.BNC1, 0),
                (Bpod.OutputChannels.BNC2, 255),
            ])
