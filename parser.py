# HELPER FUNCTIONS FOR PARSING MALLET FILES AND QUALAROO QUERIES
import numpy as np
import csv
from datetime import datetime

def parse_docs(File):
    '''
    Takes mallet doc_topics file and parses into a list of lists of tuples:
    [doc1[(topic number,topic weight), (ect.)], doc2[(topic number,weight),()]] 
    The tuples within each doc list are sorted by topic number
    The order that mallet outputs the doc-topics file is the same order that
    was given as the input, i.e the same order as whatever was queried from mongo.
    '''
    with open(File) as docFile:
        strings = docFile.read().split('\n')
    strings = strings[1:]
    docs = []
    for line in strings:
        if line !="":
            temp = line.split()
            values = []
            for i in range((len(temp)-2)/2):
                values.append((int(temp[2*i+2]),float(temp[2*i+3])))
            values.sort()
            docs.append(values)
    return docs


def parse_dates(dateFile):
    '''
    Removes the time portion of the timestamp
    Should only leave the date portion eg,
    '2014-07-14-T03:55:45.000Z' becomes
    '2014-07-14', and then it divides each month into 2 two week periods
    The final time stamp is an integer, where the last digit is 0 for the first 
    2- week period and 1 for the second eg. 2014-07-10 becomes 2014070 and 
    2014-07-23 becomes 2014071. These dates are used only for ordering so 
    linearity is not an issue. From here on out "date" will refer to this timestamp
    The timestamp should be in the 2nd column   
    '''
   

    
    with open(dateFile) as File:
        reader =  csv.reader(File, delimiter=',')
        coms = []
        times = []
        for line in reader:
            coms.append(line[0])
            times.append(line[1])


    days = []          
    date_format = "%d-%m-%Y"
    for each in times:
        y = each[0:4]
        m = each[5:7]
        d = each[8:10]
        date_string = '%s-%s-%s'% (d,m,y)
        num = datetime.strptime(date_string, date_format)
        days.append(num)
        

    return days

def parse_mongo(selection):
    '''
    Parses a mongo selection for doc_topics and dates. 
    Returns list of lists in order of selection for doc_topics,
    and list of datetime objects for dates, in order of selection
    '''
    
    docs = []
    days = []          
    date_format = "%d-%m-%Y"
    for log in selection:
        docs.append([float(weight) for weight in log['topics'].split(',')])
        time = log['timestamp']
        y = time[0:4]
        m = time[5:7]
        d = time[8:10]
        date_string = '%s-%s-%s'% (d,m,y)
        date = datetime.strptime(date_string, date_format)
        days.append(date)
    return docs, days
    
def parse_df(data):
    docs = np.array(data['topics'])
    days = np.array(data['timestamp'])
    date_format = "%Y-%m-%d"
    for i in range(len(data)):        
        date_string = days[i][:10]
        days[i] = datetime.strptime(date_string, date_format)
    return docs, days
    
def get_keys(keysFile):
    '''
    Parses mallet topic-keys file for the alpha value of each topic
    Returns np.array, assumes that the correct file is mallet/Master/keys/txt
    '''
    with open(keysFile) as File:
        reader = csv.reader(File,delimiter='\t')
        alpha = []
        for line in reader:
            alpha.append(float(line[1]))    
    return np.array(alpha)


def get_scores(File):
    '''
    Parses csv file that contains the score of each comment in 5th column
    Returns list. The order will be the same as the input file, which should be 
    the same as doc_topics from mallet
    '''
    with open(File) as scoreFile:
        reader =  csv.reader(scoreFile, delimiter=',')
        coms = []
        scores = []
        i = 0
        for line in reader:
            if i == 0:
                pass
            else:   
                coms.append(line[0])
                scores.append(float(line[-1]))
            i += 1
    if scores[0] in [1.,2.,3.,4.,5.]:
        return scores
    else:
        print "ERROR: scores need to be in the last column, or you can change this code"
        return 



