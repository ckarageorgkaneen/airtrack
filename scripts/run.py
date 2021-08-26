#!/usr/bin/env python3
import logging
import argparse

from airtrack.settings import AIRTRACK_LOG_LEVEL

from airtrack.src import Airtrack

logging.basicConfig(level=AIRTRACK_LOG_LEVEL)

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--trials', type=int, help='Number of trials.')


def run(trials):
    airtrack = Airtrack()
    airtrack.run(trials=trials)


if __name__ == '__main__':
    args = parser.parse_args()
    run(trials=args.trials)
