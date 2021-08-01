import logging
import time

from airtrack.src.definitions.actuator import AirtrackActuatorState
from airtrack.src.errors import AirtrackActuatorError
from airtrack.src.errors import on_error_raise

from pybpodapi.protocol import Bpod

logger = logging.getLogger(__name__)

handle_error = on_error_raise(AirtrackActuatorError, logger)


class AirtrackActuator:

    LOW = 0
    HIGH = 255
    STATE = AirtrackActuatorState
    PULL_BLOCKING_WAIT = 10

    def __init__(self, bpod):
        self._bpod = bpod
        self._current_state = self.STATE.AT_REST
        self._peek_enabled = True
        self.__peek_push_start_time = None
        self.__peek_push_elapsed_time = None
        self.__peek_push_timeout = None
        self.__peek_at_rest_start_time = None
        self.__peek_at_rest_elapsed_time = None
        self.__peek_at_rest_timeout = None

    @property
    def _peek_push_start_time(self):
        return self.__peek_push_start_time

    @_peek_push_start_time.setter
    def _peek_push_start_time(self, value):
        if value is None:
            self.__peek_push_start_time = None
        elif self._peek_push_start_time is None:
            self.__peek_push_start_time = value

    @property
    def _peek_push_elapsed_time(self):
        return self.__peek_push_elapsed_time

    @_peek_push_elapsed_time.setter
    def _peek_push_elapsed_time(self, value):
        if value is None:
            self.__peek_push_elapsed_time = None
        elif self._peek_push_elapsed_time is None:
            self.__peek_push_elapsed_time = value
        elif value != 0:
            self.__peek_push_elapsed_time = value

    @property
    def _peek_push_timeout(self):
        return self.__peek_push_timeout

    @_peek_push_timeout.setter
    def _peek_push_timeout(self, value):
        if value is None:
            self.__peek_push_timeout = None
        elif self._peek_push_timeout is None:
            self.__peek_push_timeout = value

    @property
    def _peek_at_rest_start_time(self):
        return self.__peek_at_rest_start_time

    @_peek_at_rest_start_time.setter
    def _peek_at_rest_start_time(self, value):
        if value is None:
            self.__peek_at_rest_start_time = None
        elif self._peek_at_rest_start_time is None:
            self.__peek_at_rest_start_time = value

    @property
    def _peek_at_rest_timeout(self):
        return self.__peek_at_rest_timeout

    @_peek_at_rest_timeout.setter
    def _peek_at_rest_timeout(self, value):
        if value is None:
            self.__peek_at_rest_timeout = None
        elif self._peek_at_rest_timeout is None:
            self.__peek_at_rest_timeout = value

    @property
    def _peek_at_rest_elapsed_time(self):
        return self.__peek_at_rest_elapsed_time

    @_peek_at_rest_elapsed_time.setter
    def _peek_at_rest_elapsed_time(self, value):
        if value is None:
            self.__peek_at_rest_elapsed_time = None
        elif self._peek_at_rest_elapsed_time is None:
            self.__peek_at_rest_elapsed_time = value
        elif value != 0:
            self.__peek_at_rest_elapsed_time = value

    def _reset_peek_times(self):
        self.__peek_push_start_time = None
        self.__peek_push_elapsed_time = None
        self.__peek_push_timeout = None
        self.__peek_at_rest_start_time = None
        self.__peek_at_rest_elapsed_time = None
        self.__peek_at_rest_timeout = None

    def _peek_push_timed_out(self):
        return self._peek_push_elapsed_time >= self._peek_push_timeout

    def _peek_at_rest_timed_out(self):
        return self._peek_at_rest_elapsed_time >= self._peek_at_rest_timeout

    @handle_error
    def _trigger_bnc_output(self, channel_number, value):
        self._bpod.manual_override(
            channel_type=Bpod.ChannelTypes.OUTPUT,
            channel_name=Bpod.ChannelNames.BNC,
            channel_number=channel_number,
            value=value,
            ignore_emulator=True)

    def _trigger_ok(self, state, desired_state):
        return state == desired_state and self._current_state != desired_state

    def _trigger_rest(self):
        self._trigger_bnc_output(channel_number=1, value=self.LOW)
        self._trigger_bnc_output(channel_number=2, value=self.LOW)

    def _trigger_push(self):
        self._trigger_bnc_output(channel_number=1, value=self.HIGH)
        self._trigger_bnc_output(channel_number=2, value=self.LOW)

    def _trigger_pull(self):
        self._trigger_bnc_output(channel_number=1, value=self.LOW)
        self._trigger_bnc_output(channel_number=2, value=self.HIGH)

    def _trigger(self, state):
        if self._trigger_ok(state, self.STATE.AT_REST):
            self._trigger_rest()
            self._current_state = self.STATE.AT_REST
        elif self._trigger_ok(state, self.STATE.PUSHING):
            self._trigger_push()
            self._current_state = self.STATE.PUSHING
        elif self._trigger_ok(state, self.STATE.PULLING):
            self._trigger_pull()
            self._current_state = self.STATE.PULLING

    def rest(self):
        self._trigger(self.STATE.AT_REST)

    def push(self):
        self.rest()
        self._trigger(self.STATE.PUSHING)

    def pull(self, block=False):
        self._reset_peek_times()
        self._peek_enabled = True
        self.rest()
        self._trigger(self.STATE.PULLING)
        if block:
            time.sleep(self.PULL_BLOCKING_WAIT)

    def peek(self, push_timeout, at_rest_timeout=0):
        self._peek_push_timeout = push_timeout
        self._peek_push_elapsed_time = 0
        self._peek_at_rest_timeout = at_rest_timeout
        self._peek_at_rest_elapsed_time = 0
        push_timed_out = self._peek_push_timed_out()
        at_rest_timed_out = self._peek_at_rest_timed_out()
        if at_rest_timed_out:
            self.pull()
            self._peek_enabled = False
        elif push_timed_out:
            self._peek_at_rest_start_time = time.time()
            self.rest()
            self._peek_at_rest_elapsed_time = time.time() - \
                self._peek_at_rest_start_time
        elif self._peek_enabled:
            self._peek_push_start_time = time.time()
            self.push()
            self._peek_push_elapsed_time = time.time() - \
                self._peek_push_start_time

    def reset(self):
        self.pull()
