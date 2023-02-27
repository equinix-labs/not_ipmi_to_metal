#!/bin/bash

#This script it ugly / hacky AF, it was a total rush job

while getopts "h:u:p:i:o:k:t" option; do
   case $option in
		h) IPMI_HOST=$OPTARG;;
		u) IPMI_USER=$OPTARG;;
		p) IPMI_PASS=$OPTARG;;
		i) IN_FILE=$OPTARG;;
		o) OUT_FILE=$OPTARG;;
		k) NETFN_KEY=$OPTARG;;
		t) NETFN_KEY=$OPTARG;;		
   esac
done

#NETFN_KEY="haha2"

echo 'haha'
echo $IPMI_HOST
echo $NETFN_KEY

cat $IN_FILE | while read line
do
	((COUNTER++))
	#echo $line
	if [[ $line =~ "netfn   :" ]]; then
		echo $line
		NETFN=$(echo $line | awk '{print$NF}')
		echo $NETFN
		CURSOR=$COUNTER
		((CURSOR++))
		if [[ $NETFN = $NETFN_KEY ]]; then
			CMD=$(sed -n ${CURSOR}p $IN_FILE | awk '{print$NF}')
			#echo "cmd is"
			#echo $CMD
			((CURSOR++))
			DATA=$(sed -n ${CURSOR}p $IN_FILE | awk -F ':' '{print$NF}')
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
