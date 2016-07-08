#!/bin/bash

# Info for tests:

# running multiple consoles for hosts, and run all 2 all $IPERF:
#mininet/examples/consoles.py

# runni mininedit, can run with custom topo, and start cli:
#mininet/examples/mininedit.py

# nice way to connect to hosts and start $IPERF:
#xterm  -e "~/mininet/util/m h1 $IPERF -s -t -i 1 & sleep 10; sudo killall $IPERF" & sleep 1 ;  xterm  -e "~/mininet/util/m h2 $IPERF -c 10.0.0.1 -i 1"
# or :
#rm -rf /tmp/tmp.log; T=35; xterm -hold  -e "~/mininet/util/m h1 $IPERF -s -t $T  -i 1 >> /tmp/tmp.log & sleep $T ; sudo killall $IPERF" & sleep 1 ;  xterm -hold  -e "~/mininet/util/m h2 $IPERF -c 10.0.0.1 -t $T -i 1 -o /tmp/c.log >> /tmp/tmp.log" &

# watch results:
#clear; while [[ 1 ]] ; do cat /tmp/tmp.log | tail -n 10; sleep 3; clear; done


#
#  Tests:
#  - use UDP (-u) traffic for reiliable reports, for both sides
#  - add paralell process (-P) for creating the requires BW. grep for SUM.
#  - dont use miniedit



function Use {
    echo "Usage: %0 <>"
}

SWITCHES=( )
HOSTS=( )


# processing params:
for host in $@; do
    HOSTS=( ${HOSTS[@]} $host )
done


function host_to_ip {
    echo "10.0.0.$1"
}

export LC_ALL=C


DEBUG_MOD=0
NUM_CONNECTIONS=$(( ((  (( ${#HOSTS[@]} * ${#HOSTS[@]} )) - ${#HOSTS[@]} )) / 2  ))
TIME=$((  NUM_CONNECTIONS * 3 ))
WAIT_TIME=40
BASE_DIR="/home/mininet/optical_network"
TEST_DIR=${BASE_DIR}"/perftest_logs"
SUMMARY_FILE=$TEST_DIR"/summary.log"
IPERF_LOGS_DIR=$TEST_DIR"/iperf_logs"
LOG_FILE=${IPERF_LOGS_DIR}"/iperf"
CON_FILE=${LOGS_DIR}"con"
HOST_CMD="/home/mininet/mininet/util/m"


function cleanup {
    if [[ ! -d $TEST_DIR ]] ;then
        mkdir $TEST_DIR
    fi
    sudo rm -rf ${TEST_DIR}/*
    mkdir $IPERF_LOGS_DIR
}

sudo chmod -R 777 $BASE_DIR

xterm_params=" -hold -geometry 70x80"

START_TIME=$SECONDS

function print_timer {
    echo $(( $SECONDS - $START_TIME  ))
}

function reset_timer {
    START_TIME=$SECONDS
}

# TCP_PROCESSES * CONNECTION_MBITS = CAPACITY_TO_MBITS
# tcp_processes should be > 1
TCP_PROCESSES=2
CONNECTION_MBITS=5
IPERF="iperf3"
#PROTO="-u"
PROTO=""
if [[ $IPERF == "iperf" ]]; then
    iperf_client_params="-t $TIME -i 1 -P $TCP_PROCESSES $PROTO  -f m"
    iperf_server_params="-t $TIME -i 1 -P $TCP_PROCESSES -f m"
else # iperf3
    iperf_client_params="-t $TIME -i 1 -b ${CONNECTION_MBITS}mb  -P $TCP_PROCESSES $PROTO -f m"
    iperf_server_params="-i 1"
fi

function runAll2AllIPerf {
    sudo killall $IPERF > /dev/null
    port=5000
    for host1 in ${HOSTS[@]}; do
        for host2 in ${HOSTS[@]}; do
            if (( $host2 >= $host1 )) ; then
                break
            fi
            server_log_file="${LOG_FILE}_${host1}_from_${host2}"
            rm -f $server_log_file
            port=$(( port + 1 ))
            filter="" #; | cut -d\"t\" -f 2-  "
            if (( $DEBUG_MOD > 1 )); then
                #xterm $xterm_params  -e "echo HELLO ; $HOST_CMD h$host1 $IPERF -s $iperf_server_params -p $port | tee ${server_log_file}" &
                server_cmd="xterm $xterm_params  -e \"$HOST_CMD h$host1 $IPERF -s $iperf_server_params -p $port |& tee ${server_log_file} \" &"
            else
                server_cmd="$HOST_CMD h$host1 $IPERF -s $iperf_server_params -p $port |& tee ${server_log_file} > /dev/null &"
            fi
            eval $server_cmd
        done
    done

    sleep 2
    port=5000
    process_num=1
    for host1 in ${HOSTS[@]}; do
        for host2 in ${HOSTS[@]}; do
            if (( $host2 >= $host1 )) ; then
                break
            fi
            #server_log_file="${LOG_FILE}_${host1}_from_${host2}"
            port=$(( port + 1 ))
            filter="" #; | cut -d\"t\" -f 2-  "
            client_log_file="${LOG_FILE}_${host2}_to_${host1}"
            server_log_file="${LOG_FILE}_${host1}_from_${host2}"
            rm -f $client_log_file
            if (( $DEBUG_MOD > 0 )); then
                client_cmd="xterm $xterm_params  -e \"$HOST_CMD h$host2 $IPERF -c `host_to_ip $host1` $iperf_client_params -p $port |& tee ${client_log_file}\" &"
            else
                client_cmd="$HOST_CMD h$host2 $IPERF -c `host_to_ip $host1` $iperf_client_params -p $port |& tee ${client_log_file} > /dev/null  &"
            fi
            is_listen=""
            while (( ($SECONDS - $START_TIME) <= $TIME )); do
                sleep 0.1
                is_listen=`cat $server_log_file | grep listening `
                if [[ $is_listen != "" ]]; then
                    break
                fi
            done
            #  with iperf3 we have no idea if server started listening ...
            if [[ $IPERF == "iperf" ]]; then
                if [[ $is_listen == "" ]]; then
                    echo "FATAL error in connection ${host2}_to${host1}: server is not listening! "
                fi
            fi
            #echo "`print_timer`: $client_cmd"
            echo -n "`print_timer`:$process_num , "
            process_num=$(( process_num + 1 ))
            eval $client_cmd
        done
    done

}


function collectResults {
    echo "**** Summary ***" > $SUMMARY_FILE
    for host1 in ${HOSTS[@]}; do
        for host2 in ${HOSTS[@]}; do
            if (( $host2 >= $host1 )) ; then
                break
            fi
            server_log_file="${LOG_FILE}_${host1}_from_${host2}"
            client_log_file="${LOG_FILE}_${host2}_to_${host1}"
            #echo $server_log_file
            #cat $server_log_file | grep SUM | tail -n 5 | head -n 1
            echo -n "${host2}_to_${host1}," >> $SUMMARY_FILE
            is_failed=`cat $client_log_file | egrep "failed|unable"`
            bw=`cat $client_log_file | grep SUM | tail -n 5 | head -n 1 | tr -s ' ' | cut -d's' -f3- | cut -d'b' -f1 | cut -d' ' -f2`
            if [[ $is_failed != "" ]] || [[ $bw == ""  ]] ; then
                echo "fail" >> $SUMMARY_FILE
            else
                echo $bw >> $SUMMARY_FILE
            fi
        done
    done
    echo "***********" >> $SUMMARY_FILE
    #sudo killall $IPERF >& /dev/null

}

function test2 {
    cleanup
    runAll2AllIPerf
    sleep $WAIT_TIME
    #reset_timer
    sudo killall $IPERF >& /dev/null
    sudo killall mnexec >& /dev/null
    sleep 5
    collectResults
    cat $SUMMARY_FILE

}

test2

paste_files_logs=""
paste_files_cons=""

function runAll2AllIPerfOnline {
    echo "hosts: ${HOSTS[@]}"
    for host1 in ${HOSTS[@]}; do
        for host2 in ${HOSTS[@]}; do
            if (( $host1 >= $host2 )) ; then
                continue
            fi
            con="${host2}_to_${host1}"
            log_file="${LOG_FILE}_${con}"
            log_file_tmp="${log_file}.tmp"
            con_file="${CON_FILE}_${con}"
            rm -f $log_file $con_file
            echo "$con     " > $con_file
            paste_files_logs="${paste_files_logs} ${log_file}"
            paste_files_cons="${paste_files_cons} ${con_file}"
            echo "running $IPERF $host1 -> $host2"
            port=$(( port + 1 ))
            filter="" #; | cut -d\"t\" -f 2-  "
            echo "" > $log_file
            cmd="xterm $xterm_params  -e \"$HOST_CMD h$host1 $IPERF -s $iperf_params -p $port $filter > /dev/null \" & sleep 0.3 ;  xterm $xterm_params  -e \"$HOST_CMD h$host2 $IPERF -c `host_to_ip $host1` $iperf_params -p $port  | tee ${log_file_tmp} &  while [[ 1 ]]; do sleep 1 ; cat $log_file_tmp |& tr -s  ' ' |& cut -d ' ' -f 7- |& tee  ${log_file} ; done \" &"

            echo $cmd
            eval $cmd
        done
    done
}


function showResults {
    clear
    while [[ 1 ]] ; do
        #for host in ${HOSTS[@]}; do
        #    cat ${LOG_FILE}${host} | tail -n $(( ${#HOSTS[@]} * 5 ))
        #done
        paste $paste_files_cons
        echo "-------------------------------------- "
        paste $paste_files_logs | tail -n 10
        sleep 3
        clear
    done
}



function test1 {
    runAll2AllIPerfOnline
    sleep 2
    showResults
}



echo "Done!"


