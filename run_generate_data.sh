#!/bin/bash
echo; echo; echo 'Be sure you are running this script on the same machine as the DB is on, for best performance!'; echo; echo;
mkdir -p logs
cd logs
DATE=$(date)
touch "$DATE".txt
echo "Log file created shortly after $DATE."
echo "Log file created shortly after $DATE." >> "$DATE".txt
echo "Running generate_data.py..." >> "$DATE".txt
ENV="DEBUG" python3 ../generate_data.py 2>&1 >> "$DATE".txt
# ENV="DEBUG" python ../generate_data_py2.py 2>&1 >> "$DATE".txt
DATE2=$(date)
echo "generate_data.py finished running by $DATE2." >> "$DATE".txt