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

from airtrack.src.sma import AirtrackStateMachine
from airtrack.src.errors import on_error_raise
from airtrack.src.errors import AirtrackError

from pybpodapi.protocol import Bpod

logger = logging.getLogger()

handle_error = on_error_raise(AirtrackError, logger)


class Airtrack:
    """Airtrack system interface."""

    def __init__(self):
        self._bpod = Bpod(emulator_mode=True)
        self._bpod.open()
        self._sma = AirtrackStateMachine(self._bpod)
        self._sma_setup()
        # Register exit handler
        atexit.register(self.close)

    @handle_error
    def _close(self):
        self._bpod.close(ignore_emulator=True)

    @handle_error
    def _run(self):
        self._bpod.send_state_machine(
            self._sma, ignore_emulator=True)
        self._bpod.run_state_machine(self._sma)

    @handle_error
    def _sma_setup(self):
        self._sma.setup()

    @handle_error
    def _sma_clean_up(self):
        self._sma.clean_up()

    def run(self):
        """Run the system."""
        self._run()

    def close(self):
        """Close the system."""
        self._sma_clean_up()
        self._close()
