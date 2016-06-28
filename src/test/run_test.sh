#!/bin/bash

# Info for tests:

# running multiple consoles for hosts, and run all 2 all iperf:
#mininet/examples/consoles.py

# runni mininedit, can run with custom topo, and start cli:
#mininet/examples/mininedit.py

# nice way to connect to hosts and start iperf:
#xterm  -e "~/mininet/util/m h1 iperf -s -t -i 1 & sleep 10; sudo killall iperf" & sleep 1 ;  xterm  -e "~/mininet/util/m h2 iperf -c 10.0.0.1 -i 1"
# or :
#rm -rf /tmp/tmp.log; T=35; xterm -hold  -e "~/mininet/util/m h1 iperf -s -t $T  -i 1 >> /tmp/tmp.log & sleep $T ; sudo killall iperf" & sleep 1 ;  xterm -hold  -e "~/mininet/util/m h2 iperf -c 10.0.0.1 -t $T -i 1 -o /tmp/c.log >> /tmp/tmp.log" &

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

HOST_CMD="~/mininet/util/m"
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
TIME=$((  NUM_CONNECTIONS * 6 ))
#WAIT_TO_SERVER=0.7
BASE_DIR="/home/mininet/optical_network/test_logs/"
LOGS_DIR=$BASE_DIR"iperf_logs/"
LOG_FILE=${LOGS_DIR}"iperf"
CON_FILE=${LOGS_DIR}"con"


if [[ ! -d $BASE_DIR ]] ;then
    mkdir $BASE_DIR
fi

if [[ ! -d $LOGS_DIR ]] ;then
    mkdir $LOGS_DIR
fi

sudo chmod -R 777 $BASE_DIR

xterm_params=" -hold -geometry 200x150"

START_TIME=$SECONDS

function print_time {
    echo $(( $SECONDS - $START_TIME  ))
}


function runAll2AllIPerf {
    sudo killall iperf > /dev/null
    iperf_params="-t $TIME -i 1  -P 5 -f m"
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

            #client_log_file="${LOG_FILE}_${host2}_to_${host1}"
            #server_cmd="xterm $xterm_params  -e \"$HOST_CMD h$host1 iperf -s                     $iperf_params -p $port |& tee ${server_log_file}\" &"
            server_cmd="$HOST_CMD h$host1 iperf -s                     $iperf_params -p $port |& tee ${server_log_file} > /dev/null &"
            #client_cmd="xterm $xterm_params  -e \"$HOST_CMD h$host2 iperf -c `host_to_ip $host1` $iperf_params -p $port |& tee ${client_log_file}\" &"
            #client_cmd="$HOST_CMD h$host2 iperf -c `host_to_ip $host1` $iperf_params -p $port |& tee ${client_log_file} > /dev/null  &"
            eval $server_cmd
        done
    done

    sleep 2
    port=5000
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
            #server_cmd="xterm $xterm_params  -e \"$HOST_CMD h$host1 iperf -s                     $iperf_params -p $port |& tee ${server_log_file}\" &"
            #server_cmd="$HOST_CMD h$host1 iperf -s                     $iperf_params -p $port |& tee ${server_log_file} > /dev/null &"
            #client_cmd="xterm $xterm_params  -e \"$HOST_CMD h$host2 iperf -c `host_to_ip $host1` $iperf_params -p $port |& tee ${client_log_file}\" &"
            client_cmd="$HOST_CMD h$host2 iperf -c `host_to_ip $host1` $iperf_params -p $port |& tee ${client_log_file} > /dev/null  &"
            while (( ($SECONDS - $START_TIME) <= $TIME )); do
                sleep 0.1
                is_listen=`cat $server_log_file | grep listening `
                if [[ $is_listen != "" ]]; then
                    break
                fi

            done
            echo "`print_time`: $client_cmd"
            eval $client_cmd
        done
    done

}

SUMMARY_FILE=$BASE_DIR"summary.log"

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
            is_failed=`cat $client_log_file | grep failed`
            bw=`cat $client_log_file | grep SUM | tail -n 5 | head -n 1 | tr -s ' ' | cut -d's' -f3- | cut -d'b' -f1 | cut -d' ' -f2`
            if [[ $is_failed != "" ]] || [[ $bw == ""  ]] ; then
                echo "fail" >> $SUMMARY_FILE
            else
                echo $bw >> $SUMMARY_FILE
            fi
        done
    done
    echo "***********" >> $SUMMARY_FILE
    sudo killall iperf > /dev/null

}

function test2 {
    runAll2AllIPerf
    sleep $TIME
    sudo killall -9 iperf
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
            echo "running iperf $host1 -> $host2"
            port=$(( port + 1 ))
            filter="" #; | cut -d\"t\" -f 2-  "
            echo "" > $log_file
            cmd="xterm $xterm_params  -e \"$HOST_CMD h$host1 iperf -s $iperf_params -p $port $filter > /dev/null \" & sleep 0.3 ;  xterm $xterm_params  -e \"$HOST_CMD h$host2 iperf -c `host_to_ip $host1` $iperf_params -p $port  | tee ${log_file_tmp} &  while [[ 1 ]]; do sleep 1 ; cat $log_file_tmp |& tr -s  ' ' |& cut -d ' ' -f 7- |& tee  ${log_file} ; done \" &"

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


