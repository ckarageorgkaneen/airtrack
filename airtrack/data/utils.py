import os

import airtrack

from airtrack.submodules.sttp.sttp import STTP

from pybpodapi.protocol import Bpod

STATE_TRANSITION_TABLE_FILENAME = 'state_transition_table.csv'
STATE_DIAGRAM_FILENAME = 'state_diagram.png'
STATE_TRANSITION_TABLE_FILE = os.path.join(
    os.path.dirname(__file__), STATE_TRANSITION_TABLE_FILENAME)


def list_bpod_events():
    return [e for e in dir(Bpod.Events)
            if e[0].isupper() and not callable(getattr(Bpod.Events, e))]


def list_bpod_serial_events(blacklist=[]):
    return [e for e in list_bpod_events()
            if e.startswith('Serial') and e not in blacklist]


def read_state_transition_table():
    """Parse state transition table and return dictionary of state transitions.

    :rtype: ``dict``
    """
    sttp = STTP(stt_csv_file=STATE_TRANSITION_TABLE_FILE)
    resources_dir = os.path.join(
        os.path.dirname(airtrack.__path__.__dict__['_path'][0]),
        'resources')
    state_machine_file = os.path.join(
        resources_dir, STATE_DIAGRAM_FILENAME)
    sttp.visualize(filename=state_machine_file, format='png')
    return sttp.dictify()


def bpodify_state_transition_table():
    """Replace (non-Bpod) state transition events with Bpod protocol Serial
    events and return dictionary of state transitions.

    :rtype: ``dict``
    """
    state_transitions = read_state_transition_table()
    bpodified_state_transitions = {}
    bpod_events = list_bpod_events()
    transition_events = [event for transition in state_transitions.values()
                         for event in transition.values()]
    available_bpod_serial_events = list_bpod_serial_events(
        blacklist=transition_events)
    available_bpod_serial_events.sort(
        key=lambda e: int(e.split('_')[0][-1] + e.split('_')[1]))
    for source_state, transition in state_transitions.items():
        new_transition = bpodified_state_transitions[source_state] = {}
        for dest, event in transition.items():
            if event in bpod_events:
                new_transition[dest] = event
            elif event.startswith('(') and event.endswith(')'):
                # Add state timer integer value (seconds)
                for c in event.split():
                    if c.isnumeric():
                        new_transition[dest] = float(c)
            else:
                # Replace event with an available bpod serial event
                new_transition[dest] = available_bpod_serial_events.pop(0)
    return bpodified_state_transitions
