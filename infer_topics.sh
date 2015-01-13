#!/usr/bin/env bash

cd ../mallet

bin/mallet import-file --input ../texts/qualaroo_comments.txt --keep-sequence \
--use-pipe-from Master/feature_vecs.mallet --output Master/infered_vecs.mallet 



bin/mallet infer-topics --input Master/infered_vecs.mallet --inferencer \
Master/inferencer.mallet  --output-doc-topics Master/doc_topics.txt

python - <<END

print "COMBINNG MALLET OUTPUT WITH CLEAN DATA FROM SAWYER"
import csv
import os
import sys
sys.path.insert(0, '../')
from utils import parser

p = os.path.abspath('..')
mallet_data = parser.parse_docs(p+'/mallet/Master/doc_topics.txt')
inFile =  open(p+'/texts/qualaroo_all.txt')
reader = csv.reader(inFile, delimiter=',') 
sawyer_data = []
i = 0
for line in reader:
    if i == 0:
        header = line
    else:
        sawyer_data.append(line)
    i += 1
inFile.close()

outFile = open(p+'/texts/qualaroo_csv.txt','w') 
writer = csv.writer(outFile, delimiter=',')
header = header+['topics']
print '''This is the csv header that will be used for pandas DataFrame, or mongodb, 
the output from sawyer must be in this order: %s''' % header

writer.writerow(header)

i = 0
for line in sawyer_data:
    temp = ','.join([str(weight) for num,weight in mallet_data[i]])
    line.append(temp)
    writer.writerow(line)
    i += 1

inFile.close()
outFile.close()  
END

