#!/usr/bin/env python3
import atexit

from state_machine import AirtrackStateMachine

from pybpodapi.protocol import Bpod


class Airtrack:
    def __init__(self, emulate=True):
        self._bpod = Bpod(emulator_mode=True)
        self._emulate = emulate
        if not self._emulate:
            self._bpod.open()
        # Register exit handler
        atexit.register(self.close)
        self._sma = AirtrackStateMachine(self._bpod)
        self._sma.setup()

    def close(self):
        self._bpod.close(ignore_emulator=not self._emulate)

    def run(self):
        self._bpod.send_state_machine(
            self._sma, ignore_emulator=not self._emulate)
        self._bpod.run_state_machine(self._sma)


if __name__ == '__main__':
    Airtrack(emulate=False).run()
