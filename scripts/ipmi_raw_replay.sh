#!/bin/bash

# This script ingests the output of a "-vv" ipmi call, and replays it with raw calls and records the raw commands
# This functionally lets us collect the back and forth stream of an ipmi call
# example: ipmitool -vv -I lanplus -H 10.250.31.122 -U ADMIN -P ADMIN fru print 0 > /tmp/ipmi_out 2>&1

COUNTER=0

IPMI_HOST="10.250.31.122"
IPMI_USER="ADMIN"
IPMI_PASS="ADMIN"
IN_FILE="/tmp/ipmi_out"
NETFN_KEY="0x0a"
OUT_FILE="/tmp/ipmi_replay_out"

echo "Starting replay at `date`" > $OUT_FILE

cat $IN_FILE | while read line
do
	((COUNTER++))
	if [[ $line =~ "netfn   :" ]]; then
		NETFN=$(echo $line | awk '{print$NF}')
		#echo $NETFN
		CURSOR=$COUNTER
		((CURSOR++))
		if [[ $NETFN = $NETFN_KEY ]]; then
			CMD=$(sed -n ${CURSOR}p /tmp/ipmi_out | awk '{print$NF}')
			#echo "cmd is"
			#echo $CMD
			((CURSOR++))
			DATA=$(sed -n ${CURSOR}p /tmp/ipmi_out | awk -F ':' '{print$NF}')
			#echo "data cursor is $CURSOR"
			echo "NETFN is $NETFN , CMD is $CMD, DATA is $DATA" | tee -a $OUT_FILE
			echo "command being run is: ipmitool -I lanplus -H $IPMI_HOST -U $IPMI_USER -P $IPMI_PASS raw $NETFN $CMD $DATA >> $OUT_FILE" | tee -a $OUT_FILE
			ipmitool -I lanplus -H $IPMI_HOST -U $IPMI_USER -P $IPMI_PASS raw $NETFN $CMD $DATA >> $OUT_FILE
			# some lifecycle controllers don't want to work that hard, we're going to sleep to be nice
			sleep 2
		else
			((CURSOR++))
		fi
	fi	
done