#!/bin/bash

function Use {
    echo "Usage: $0 <file> <phrase>"
    exit
}

if (( $# < 2 )); then
    Use
fi

POLLING_FILE=$1
POLLING_PHRASE=$2

function poll {
    prev_lines=0
    while [[ 1 ]]; do
        sleep 1
        lines=`cat $POLLING_FILE | wc -l`
        if (( $lines > $prev_lines )); then
            clear
            cat $POLLING_FILE |& egrep $POLLING_PHRASE
            prev_lines=$lines
        fi
    done
}


poll


