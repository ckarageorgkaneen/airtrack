from enum import Enum

AirtrackState = Enum('AirtrackState', [
    'INITIATE',
    'QUERY_SUBJECT_LOCATION',
    'ENTER_LANE',
    'EXIT_LANE'
])
