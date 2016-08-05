#!/bin/bash

GRAPHS_DIR="graphs"

function showGraphs {
    ls $GRAPHS_DIR | while read _file; do
        echo "$_file:"
        cat "${GRAPHS_DIR}/${_file}"
        printf  "+++++++++++++++++\n\n"
    done
}

showGraphs
