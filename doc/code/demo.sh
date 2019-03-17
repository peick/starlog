#!/bin/bash
#
# Execute all combinations
#

describe() {
    echo
    echo "+--------------------------------------------------------------------------"
    echo "|   $1"
    echo "+--------------------------------------------------------------------------"
    echo
}

describe "starlog.MultiprocessHandler"
python demo_multi_processing.py

describe "startlog.MultiprocessHandler in combination with starlog.StatusHandler"
python demo_multi_processing.py --status

describe "startlog.ZmqHandler"
python demo_multi_processing.py --zmq

describe "startlog.ZmqHandler in combination with starlog.StatusHandler"
python demo_multi_processing.py --status
