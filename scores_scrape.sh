#!/usr/bin/env bash

cd ..
rm texts/scores.txt

day_diff=$(( ($(date  +%s) - $(date --date="140102" +%s) )/(60*60*24) ))

for i in $(seq 1 $day_diff);
do
echo $i
let "end=(i-1)"



if [ $i -eq 1 ]; then 
    sawyer events -p qualaroo -l 100000 -f "$i days ago" -t "0 days ago" \
    "score:*" | jq -r '.[]| [.["@timestamp"], .properties.platform, .id, 
    .score] | @csv' >> texts/scores.txt
else 
    sawyer events -p qualaroo -l 100000 -f "$i days ago" -t "$end days ago" \
    "score:*" | jq -r '.[]| [.["@timestamp"], .properties.platform, .id,
    .score] | @csv' >> texts/scores.txt
fi

done


