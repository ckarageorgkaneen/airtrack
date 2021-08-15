"""Airtrack actuator base module.

This module provides an interface (AirtrackActuator) for interacting with the
linear actuator of the Airtrack system.

Example:

    import time
    from pybpodapi.protocol import Bpod
    from airtrack.src.actuator import AirtrackActuator

    bpod = Bpod(emulator_mode=True)
    bpod.open()
    aa = AirtrackActuator(bpod)

    aa.reset()  # Reset actuator position
    aa.push()  # Trigger push action
    time.sleep(3)

    aa.rest()  # Trigger rest action (stop actuator motion)
    time.sleep(3)

    aa.pull()  # Trigger pull action
    time.sleep(3)

    # Trigger peek action (must loop)
    while True:
        aa.peek()

"""
import logging
import time

from airtrack.settings import AIRTRACK_DEBUG_PREFIX
from airtrack.settings import AIRTRACK_MAX_ACTUATOR_TIMEOUT
from airtrack.settings import AIRTRACK_ACTUATOR_PUSH_TIMEOUT
from airtrack.settings import AIRTRACK_ACTUATOR_AT_REST_TIMEOUT

from airtrack.src.definitions import AirtrackActuatorState
from airtrack.src.errors import AirtrackActuatorError
from airtrack.src.errors import on_error_raise

from pybpodapi.protocol import Bpod

if AIRTRACK_ACTUATOR_PUSH_TIMEOUT > AIRTRACK_MAX_ACTUATOR_TIMEOUT or \
        AIRTRACK_ACTUATOR_AT_REST_TIMEOUT > AIRTRACK_MAX_ACTUATOR_TIMEOUT:
    raise AirtrackActuatorError(
        'Actuator push or at rest timeouts exceed maximum of'
        f'{AIRTRACK_MAX_ACTUATOR_TIMEOUT} sec.')

logger = logging.getLogger(__name__)

handle_error = on_error_raise(AirtrackActuatorError, logger)


def log_debug(message):
    logger.debug(f'{AIRTRACK_DEBUG_PREFIX} {message}')


class AirtrackActuator:
    """Airtrack linear actuator interface."""
    LOW = 0
    HIGH = 255
    STATE = AirtrackActuatorState

    def __init__(self, bpod):
        """
        :keyword  bpod:  A pybpod Bpod object
        :type     bpod:  :class:``pybpodapi.protocol.Bpod``
        """
        self._bpod = bpod
        self._current_state = self.STATE.AT_REST
        self._peek_push_enabled = True
        self._reset_peek_times()

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
        if self._peek_push_elapsed_time is None or value != 0:
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
        if self._peek_at_rest_elapsed_time is None or value != 0:
            self.__peek_at_rest_elapsed_time = value

    @property
    def _peek_pull_start_time(self):
        return self.__peek_pull_start_time

    @_peek_pull_start_time.setter
    def _peek_pull_start_time(self, value):
        if value is None:
            self.__peek_pull_start_time = None
        elif self._peek_pull_start_time is None:
            self.__peek_pull_start_time = value

    @property
    def _peek_pull_elapsed_time(self):
        return self.__peek_pull_elapsed_time

    @_peek_pull_elapsed_time.setter
    def _peek_pull_elapsed_time(self, value):
        if self._peek_pull_elapsed_time is None or value != 0:
            self.__peek_pull_elapsed_time = value

    @property
    def _peek_pull_timeout(self):
        return self.__peek_pull_timeout

    @_peek_pull_timeout.setter
    def _peek_pull_timeout(self, value):
        if self.__peek_pull_timeout is None or \
                value != 0:
            self.__peek_pull_timeout = value

    def _reset_peek_times(self):
        self.__peek_push_start_time = None
        self.__peek_push_elapsed_time = 0
        self.__peek_push_timeout = AIRTRACK_ACTUATOR_PUSH_TIMEOUT
        self.__peek_at_rest_start_time = None
        self.__peek_at_rest_elapsed_time = 0
        self.__peek_at_rest_timeout = AIRTRACK_ACTUATOR_AT_REST_TIMEOUT
        self.__peek_pull_start_time = None
        self.__peek_pull_elapsed_time = 0
        self.__peek_pull_timeout = 0

    def _peek_push_timed_out(self):
        return self._peek_push_elapsed_time >= self._peek_push_timeout

    def _peek_at_rest_timed_out(self):
        return self._peek_at_rest_elapsed_time >= self._peek_at_rest_timeout

    def _peek_pull_timed_out(self):
        return self._peek_pull_timeout == 0 or \
            self._peek_pull_elapsed_time >= self._peek_pull_timeout

    def _can_peek_rest(self):
        return self._peek_push_timed_out()

    def _can_peek_push(self):
        cannot_pull = self._peek_pull_elapsed_time == 0 or \
            self._peek_pull_timeout == 0 or \
            self._peek_pull_timed_out()
        return self._peek_push_enabled and cannot_pull

    def _can_peek_pull(self):
        return self._peek_at_rest_timed_out()

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

    def _peek_rest(self):
        self._peek_at_rest_start_time = time.time()
        self.rest()
        self._peek_at_rest_elapsed_time = time.time() - \
            self._peek_at_rest_start_time

    def _peek_push(self):
        self._peek_push_start_time = time.time()
        self.push()
        self._peek_push_elapsed_time = time.time() - \
            self._peek_push_start_time
        self._peek_pull_timeout = self._peek_push_elapsed_time

    def _peek_pull(self):
        return self.pull(enable_push=False)

    def rest(self):
        """Trigger an actuator rest action (stop motion)."""
        self._trigger(self.STATE.AT_REST)

    def push(self):
        """Trigger an actuator push action."""
        self.rest()
        self._trigger(self.STATE.PUSHING)

    def pull(self, enable_push=True):
        """Trigger an actuator pull action."""
        self._peek_pull_start_time = time.time()
        self.rest()
        self._trigger(self.STATE.PULLING)
        self._peek_pull_elapsed_time = time.time() - \
            self._peek_pull_start_time
        self._peek_push_enabled = enable_push
        if self._peek_pull_timed_out():
            pull_time_out_initialized = self._peek_pull_timeout != 0
            self._reset_peek_times()
            return pull_time_out_initialized
        return False

    def peek(self):
        """Trigger an actuator peek action.

        This method is meant to be called repeatedly, within a loop, e.g.

        while True:
            aa.peek()

        On each call, this method does one of the following:
        a. pull (if `AIRTRACK_ACTUATOR_PUSH_TIMEOUT` seconds have passed since
            first call)
        b. rest (if `AIRTRACK_ACTUATOR_AT_REST_TIMEOUT` seconds have passed
            since first call)
        c. push (if permitted)
        """
        peek_completed = False
        if self._can_peek_pull():
            log_debug('PEEK PULLING')
            peek_completed = self._peek_pull()
        elif self._can_peek_rest():
            log_debug('PEEK RESTING')
            self._peek_rest()
        elif self._can_peek_push():
            log_debug('PEEK PUSHING')
            self._peek_push()
        return peek_completed

    def reset(self):
        """Reset the actuator."""
        self.pull()
