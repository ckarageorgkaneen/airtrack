import os
import datetime
import time
import logging
from pathlib import Path

PYBPOD_API_LOG_LEVEL = logging.DEBUG
PYBPOD_API_LOG_FILE = 'pybpod-api.log'

# stream the session file to the stdin (terminal)
PYBPOD_API_STREAM2STDOUT = False
# accept commands from the stdin
PYBPOD_API_ACCEPT_STDIN = False

session_dirname = 'AIRTRACK_SESSIONS'
homepath = os.environ.get('HOMEPATH') or os.environ.get('HOME')
AIRTRACK_SESSION_PATH = os.path.join(homepath, 'Desktop', session_dirname)
Path(AIRTRACK_SESSION_PATH).mkdir(parents=True, exist_ok=True)

PYBPOD_SESSION_PATH = AIRTRACK_SESSION_PATH
PYBPOD_SESSION = datetime.datetime.fromtimestamp(
    time.time()).strftime('%Y-%m-%d %H:%M:%S')

PYBPOD_SERIAL_PORT = '/dev/ttyACM0'

# SUPPORTED BPOD FIRMWARE VERSION
# TARGET_BPOD_FIRMWARE_VERSION = "9"  # 0.7.5
# TARGET_BPOD_FIRMWARE_VERSION = "13" # 0.7.9
# TARGET_BPOD_FIRMWARE_VERSION = "15" # 0.8
# TARGET_BPOD_FIRMWARE_VERSION = "17" # 0.9
TARGET_BPOD_FIRMWARE_VERSION = "22"
EMULATOR_BPOD_MACHINE_TYPE = 3

BPOD_BNC_PORTS_ENABLED = [True, True]
BPOD_WIRED_PORTS_ENABLED = [True, True]
BPOD_BEHAVIOR_PORTS_ENABLED = [True, True, True, True, True, True, True, True]

PYBPOD_NET_PORT = None
PYBPOD_BAUDRATE = 1312500
PYBPOD_SYNC_CHANNEL = 255
PYBPOD_SYNC_MODE = 1
