#!/bin/bash

function Use {
    echo "Usage: %0 <>"
}


HOST_CMD="./mininet/util/m"
SWITCHES=( s1 s2 s3 )
HOSTS=( h1 h2 )

function PrintTable {
    sw=$1
    echo "$sw flow-table:"
    sudo ovs-ofctl dump-flows $sw | cut -d"," -f 7-
    echo ""
}


function PrintAllTables {
    for sw in ${SWITCHES[@]}; do
        PrintTable $sw
    done
}


function PrintHostARP {
    host=$1
    echo "$host ARP:"
    sudo $HOST_CMD $host arp
    echo ""
}

function PrintHostsARP {
    for host in ${HOSTS[@]}; do
        PrintHostARP $host
    done
}

function PrintHostsIPs {
    for host in ${HOSTS[@]}; do
        intf=${host}"-eth0"
        echo "$host IP:"
        sudo $HOST_CMD $host ifconfig $intf | grep inet | grep -v inet6  #  | cut -d: -f2 | awk '{print $1}'
        echo ""
    done
}

echo "Dumping..."
PrintAllTables
PrintHostsARP
PrintHostsIPs
echo "Done!"

# sudo ovs-ofctl del-flows s3
# sudo ovs-ofctl del-flows s4
# sudo ovs-ofctl del-flows s5
#
# sudo ovs-ofctl add-flow s3 ip,nw_dst=10.0.0.1,actions=output:1
# sudo ovs-ofctl add-flow s3 ip,nw_dst=10.0.0.2,actions=output:2
# sudo ovs-ofctl add-flow s4 ip,nw_dst=10.0.0.1,actions=output:2
# sudo ovs-ofctl add-flow s4 ip,nw_dst=10.0.0.2,actions=output:1
#




