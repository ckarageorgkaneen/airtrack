"""Airtrack base module.

This module provides an interface (Airtrack) for the Airtrack system.

Example:

    from airtrack.src import Airtrack

    airtrack = Airtrack()
    airtrack.run()
    airtrack.close()
"""
import logging
import atexit
import itertools

from airtrack.settings import AIRTRACK_DEBUG_PREFIX

from airtrack.src.sma import AirtrackStateMachine
from airtrack.src.subject import AirtrackSubject
from airtrack.src.errors import on_error_raise
from airtrack.src.errors import AirtrackError

from pybpodapi.protocol import Bpod

logger = logging.getLogger(__name__)

handle_error = on_error_raise(AirtrackError, logger)


class Airtrack:
    """Airtrack system interface."""

    def __init__(self):
        self.__bpod = None
        self._bpod_closed = True
        self._subject = AirtrackSubject()
        # Register exit handler
        atexit.register(self.close)

    @property
    def _bpod(self):
        if self.__bpod is None:
            self._create_bpod()
        if self._bpod_closed:
            self._open_bpod()
        return self.__bpod

    @handle_error
    def _create_bpod(self):
        self.__bpod = Bpod(emulator_mode=True)

    @handle_error
    def _open_bpod(self):
        self.__bpod.open()
        self._bpod_closed = False

    @handle_error
    def _close(self):
        self.__bpod.close(ignore_emulator=True)
        self._bpod_closed = True

    @handle_error
    def _run(self):
        self._sma = AirtrackStateMachine(self._bpod, self._subject)
        self._sma.setup()
        self._bpod.send_state_machine(self._sma, ignore_emulator=True)
        self._bpod.run_state_machine(self._sma)

    @handle_error
    def _clean_up(self):
        self._subject.clean_up()
        self._sma.clean_up()

    def run(self, trials=None):
        """Run the system.

        :keyword  trials (optional):  Number of trials to run the system for.
        :type     trials (optional):  ``int``
        """
        iterator = range(trials or 0) or itertools.count()
        for i in iterator:
            trial = i + 1
            logger.debug(f'{AIRTRACK_DEBUG_PREFIX} Starting trial #{trial}...')
            self._run()
            logger.debug(f'{AIRTRACK_DEBUG_PREFIX} End of trial #{trial}.')

    def close(self):
        """Close the system."""
        self._clean_up()
        self._close()
