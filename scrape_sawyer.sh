#!/usr/bin/env bash
cd ..

rm texts/sawyer_raw.txt

day_diff=$(( ($(date  +%s) - $(date --date="140102" +%s) )/(60*60*24) ))

for i in $(seq 1 $day_diff);
do
echo $i
let "end=(i-1)"


#Here is the loop that downloads comments and other call data for each day since January
#You can change the specific fields that you are interested in
#Keep .feedback first, and .score last in the array
#Make sure you change the header with sed appropriately

if [ $i -eq 1 ]; then 
    sawyer events -p qualaroo -l 100000 -f "$i days ago" -t "0 days ago" \
    "feedback:* && score:*" | jq -r '.[]| [.feedback, .["@timestamp"],
    .properties.endpoint_guid, .geoip.ip, .properties.platform, 
    .properties.endpoint_type, .geoip.country_code3,.enterprise, 
    .score] | @csv' >> texts/sawyer_raw.txt
else 
    sawyer events -p qualaroo -l 100000 -f "$i days ago" -t "$end days ago"\
    "feedback:* && score:*" | jq -r '.[]| [.feedback, .["@timestamp"], 
    .properties.endpoint_guid, .geoip.ip, .properties.platform, 
    .properties.endpoint_type, .geoip.country_code3, .enterprise,
    .score] | @csv' >> texts/sawyer_raw.txt
fi

done

#This python script cleans the data, removing empty comments, comments without meaning,
#words that only appear a couple of times (a changable parameter), comments with 
#Less than 2 words (also changable), and stop words
#It calls a python script in utils. This is where to look if you want to change something.
#Removing short comments reduces the total amount of comments by about 20%, 
#which may be undesireable
python - <<END 
import csv
from utils import clean_text as ct
with open('texts/sawyer_raw.txt') as File:
    reader = csv.reader(File, delimiter=',')
    coms = []
    data = []
    for line in reader:
        coms.append(line[0])
        data.append(line[1:])
    print "Processisng %d lines" % len(coms)
    cleaned = ct.clean_text(coms, data, min_length=3, min_count=4)
    ct.store_file(cleaned,'texts/qualaroo_all.txt')
    ct.store_mallet_file(cleaned, 'texts/qualaroo_comments.txt')
    
END

sed -i '1i comment,timestamp,guid,ip,platform,endpoint,country,enterprise,score' \
texts/qualaroo_all.txt



