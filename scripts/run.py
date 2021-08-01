#!/usr/bin/env python3
import logging
from airtrack.src.base import Airtrack

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    Airtrack(emulate=False).run()
