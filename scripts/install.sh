#!/usr/bin/env bash
set -e
git submodule update --init
cwd=$(pwd)
# Install pixy2
cd airtrack/submodules/pixy2
./install.sh
cd $cwd
# Install pybpod-api
pip install airtrack/submodules/pybpod-api
# Install airtrack
pip install -e .
