from enum import Enum

AirtrackState = Enum('AirtrackState', [
    'INITIATE',
    'RESET_SUBJECT_LOCATION',
    'ENTER_LANE',
    'EXIT_LANE'
])
