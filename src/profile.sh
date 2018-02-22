#!/bin/bash


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $SCRIPT_DIR


PROF_FILE="/tmp/cprof.prof"

python -m cProfile -o $PROF_FILE $@


pyprof2calltree -i $PROF_FILE -k

#### browser based
##snakeviz $PROF_FILE
