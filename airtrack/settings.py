import os
import datetime
import time
import logging
from pathlib import Path

# LOGGING
AIRTRACK_LOG_LEVEL = logging.DEBUG
AIRTRACK_DEBUG_PREFIX = '@@@@@@@@@>>>>'

# SESSIONS
homepath = os.environ.get('HOMEPATH') or os.environ.get('HOME')
session_dirname = 'AIRTRACK_SESSIONS'
session_path = os.path.join(homepath, 'Desktop', session_dirname)
Path(session_path).mkdir(parents=True, exist_ok=True)
AIRTRACK_SESSION_PATH = session_path
AIRTRACK_SESSIONS_LOG_FILE = os.path.join(
    AIRTRACK_SESSION_PATH, 'airtrack.log')
AIRTRACK_STREAM_SESSION_TO_STDOUT = False

# FILENAMES
AIRTRACK_SESSION_NAME = datetime.datetime.fromtimestamp(
    time.time()).strftime('%Y-%m-%d %H:%M:%S')

# DEVICES
AIRTRACK_BPOD_SERIAL_PORT = '/dev/ttyACM0'

# STATE MACHINE
AIRTRACK_STATE_TIMER = 0.1

# PARAMETERS
AIRTRACK_MAX_ACTUATOR_TIMEOUT = 5
AIRTRACK_ACTUATOR_PUSH_TIMEOUT = 3
# Time the actuator should remain at rest before it is pulled back
AIRTRACK_ACTUATOR_AT_REST_TIMEOUT = 3
