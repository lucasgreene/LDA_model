#!/usr/bin/env python2.7
import xml.etree.ElementTree as ET
import numpy as np
import csv
import os
import sys
sys.path.insert(0, '../')
from utils import parser



def compute_averages(docs,scores,alpha):
    '''
    First normalizes alpha and then computes the average qualaroo score
    For each topic as follows:
    Topic1_score = sum(weight_of_topic1_in_doc_i*score_of_doc_i/alpha1*total_#_comments)
    Returns np.array
    '''
    alpha = alpha/np.sum(alpha)
    counts = [0]*len(alpha)
    for i in range(len(docs)):
        score = scores[i]       
        for topic,weight in docs[i]:
            counts[topic] += (weight*score)/alpha[topic]
    
    return np.array(counts)/len(scores), alpha


def parse_print(root, alpha, counts, path):
    '''
    Parses the xml_phrase file from mallet input that contains the top 
    70 words and 70 phrases of each topic along with their weights
    Writes 70 words and top 30 phrases into csv that can be used in
    D3 word cloud
    Topics are sorted according to alpha values. Each topic number is rewritten
    To reflect the order of the topic, not the original topic number exported 
    By mallet
    '''
    ind = sorted(range(len(alpha)), key=alpha.__getitem__)[::-1]     
    alpha = alpha*100
    for child in root:

        topic = (child.attrib['id'])
        i = int(topic)
        j = ind.index(i)

        words = []
        phrases = []
        for word in child.findall('.word'):
            words.append((word.text,word.attrib['count']))
        for phrase in child.findall('.phrase'):    
            phrases.append((phrase.text,phrase.attrib['weight']))
        phrases = phrases[0:30]
        
        outfile = open(path+'/cloud/topic_words%d.csv'%j, 'w')
        outfile.write('text'+','+'size'+','+'topic'+','+'alpha'+','+'score'+','+'id'+'\n')  
        for word,size in words:
            outfile.write(word+','+size+','+str(j)+','+"%.3f"% alpha[i]+','+
                                                '%.3f'% counts[i]+','+topic+'\n')            
        for phrase,size in phrases: 
            outfile.write('_'.join(phrase.split())+','+size+','+str(j)+','+'%.3f'% alpha[i]+
                                                            ','+'%.3f'% counts[i]+topic+'\n')    
        outfile.close()
        
        
 
 
def main():
    '''
    Uses the standard mallet files stored in mallet/Master to create the csv's
    used in the d3 word cloud
    '''
    print 'CREATING WORDCLOUD CSVs'
    path = os.path.abspath('..')
    xmlFile = path+'/mallet/Master/xml_phrase_report.xml'
    docsFile = path+'/mallet/Master/doc_topics.txt'
    qualarooFile = path+'/texts/qualaroo_all.txt'
    keysFile = path+'/mallet/Master/keys.txt'
        
        
    xmlString = open(xmlFile).read()
    root = ET.fromstring(xmlString)
    docs = parser.parse_docs(docsFile)
    scores = parser.get_scores(qualarooFile)
    alpha = parser.get_keys(keysFile)
    counts,alpha = compute_averages(docs,scores,alpha)
    parse_print(root, alpha, counts, path)
    print 'DONE'
    print 'Stored files in /topics/cloud'
    
    
if __name__ == '__main__':
    main()
