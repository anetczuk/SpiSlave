#!/bin/bash


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $SCRIPT_DIR

##run particular test case: 
##			python -m unittest discover test_sss.SpiSlaveTest.test_transmission


if [ $# -gt 0 ]; then
    python -m unittest $@
else
    python -m unittest discover
fi

