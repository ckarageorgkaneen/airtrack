import atexit

from airtrack.src.sma.base import AirtrackStateMachine

from pybpodapi.protocol import Bpod


class Airtrack:
    def __init__(self, emulate=True):
        self._bpod = Bpod(emulator_mode=True)
        self._emulate = emulate
        if not self._emulate:
            self._bpod.open()
        self._sma = AirtrackStateMachine(self._bpod)
        self._sma.setup()
        # Register exit handler
        atexit.register(self.close)

    def run(self):
        self._bpod.send_state_machine(
            self._sma, ignore_emulator=not self._emulate)
        self._bpod.run_state_machine(self._sma)

    def close(self):
        self._sma.clean_up()
        self._bpod.close(ignore_emulator=not self._emulate)
