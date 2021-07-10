#!/usr/bin/env python3
from state_machine import AirtrackStateMachine
from actuator import AirtrackActuator
from subject import AirtrackSubject

from pybpodapi.protocol import Bpod


class Airtrack:
    def __init__(self, emulate=True):
        self._bpod = Bpod(emulator_mode=emulate)
        self._subject = AirtrackSubject()
        self._actuator = AirtrackActuator()
        self._sma = AirtrackStateMachine(
            self._bpod,
            self._subject,
            self._actuator)
        self._sma.setup()

    def run(self):
        self._bpod.send_state_machine(self._sma())
        self._bpod.run_state_machine(self._sma())


if __name__ == '__main__':
    Airtrack().run()
