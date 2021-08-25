#!/usr/bin/env bash
set -e
git submodule update --init
CWD=$(pwd)
SUBMODULES_TMP_FILE=$(mktemp)
git config -f .gitmodules -l 				\
	| grep path 							\
	| awk '{split($0, a, /=/); print a[2]}' \
	> $SUBMODULES_TMP_FILE
PIXY2_PATH=$(grep pixy2 $SUBMODULES_TMP_FILE)
PYBPOD_API_PATH=$(grep pybpod-api $SUBMODULES_TMP_FILE)
STTP_PATH=$(grep sttp $SUBMODULES_TMP_FILE)
rm ${SUBMODULES_TMP_FILE}
# Install pixy2
cd ${PIXY2_PATH}
./install.sh
cd ${CWD}
# Install pybpod-api
pip install -r "$PYBPOD_API_PATH/requirements.txt"
pip install -e $PYBPOD_API_PATH
# Install sttp
pip install -r "$STTP_PATH/requirements.txt"
# Install airtrack
pip install -e .
