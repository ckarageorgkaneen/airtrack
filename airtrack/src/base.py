import logging
import atexit

from airtrack.src.sma.base import AirtrackStateMachine
from airtrack.src.errors import on_error_raise
from airtrack.src.errors import AirtrackError


from pybpodapi.protocol import Bpod

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handle_error = on_error_raise(AirtrackError, logger)


class Airtrack:
    def __init__(self, emulate=True):
        self._bpod = self._Bpod()
        self._emulate = emulate
        if not self._emulate:
            self._bpod_open()
        self._sma = AirtrackStateMachine(self._bpod)
        self._sma_setup()
        # Register exit handler
        atexit.register(self.close)

    @handle_error
    def _Bpod(self):
        return Bpod(emulator_mode=True)

    @handle_error
    def _bpod_open(self):
        self._bpod.open()

    @handle_error
    def _bpod_close(self):
        self._bpod.close(ignore_emulator=not self._emulate)

    @handle_error
    def _bpod_run(self):
        self._bpod.send_state_machine(
            self._sma, ignore_emulator=not self._emulate)
        self._bpod.run_state_machine(self._sma)

    @handle_error
    def _sma_setup(self):
        self._sma.setup()

    @handle_error
    def _sma_clean_up(self):
        self._sma.clean_up()

    def run(self):
        self._bpod_run()

    def close(self):
        self._sma_clean_up()
        self._bpod_close()
