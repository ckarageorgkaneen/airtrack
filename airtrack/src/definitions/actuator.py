from enum import Enum

AirtrackActuatorState = Enum('AirtrackActuatorState', [
    'AT_REST',
    'PUSHING',
    'PULLING',
])
