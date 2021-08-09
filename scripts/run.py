#!/usr/bin/env python3
import logging

from airtrack.settings import AIRTRACK_LOG_LEVEL

from airtrack.src import Airtrack

if __name__ == '__main__':
    logging.basicConfig(level=AIRTRACK_LOG_LEVEL)
    airtrack = Airtrack()
    airtrack.run()
