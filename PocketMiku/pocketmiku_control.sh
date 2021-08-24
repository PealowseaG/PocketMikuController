#!/bin/bash
# change directory to this script being
SCRIPT_DIR=$(cd $(dirname $0); pwd)
echo "This script base directory is ""$SCRIPT_DIR"

# pocketmiku_controller after change dir of (this).sh
cd $SCRIPT_DIR
python3 pocketmiku_controller.py

# disable variable values
unset SCRIPT_DIR
# exit
exit 0
