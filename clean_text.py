# CLEANS TEXT IN CSV FORMAT
import re, csv, os
from os import path
from nltk.stem import WordNetLemmatizer
from collections import Counter
wnl=WordNetLemmatizer()



def clean_text(coms, data, min_length, min_count):
    '''
    Takes a list of comments eg. ['this is the first comment. right here', 'this is the 2nd']
    and other data as [['date'],['guid'],['ect']] 
    The function cleans the text and removes
    stopwords and lematizes. Also deletes words appearing less than 4 times
    Returns a list of lists -> ['comment','date','guid','ect']
    The function will delete comments if they are empty. Parameters min_length
    is the minimum number of words in a comment for it to get accepted. A good 
    starting value is 2. Min_count is the minimum number of times a word has 
    to appear in the entire corpus for it to get accpeted. Good value is 4.
    '''
    
    path = os.path.abspath('..')
    wordsfile = open('utils/english')
    stopwords = wordsfile.read().split()
    wordsfile.close()
    
    # This first cleaning is only for the word counts update,
    # full_string can't be put back into comment form so we will
    # have to clean the comments seperately
    print "Creating Dictionary"
    ctr = Counter()
    full_string =' '.join(coms).lower()  
    full_string = full_string.decode('ascii','ignore')  # This line is key with 'ignore', without it if we get a death threat in russian or something, we will crash on the special characters
    full_string = re.sub('sound','audio',full_string)
    full_string = re.sub('bj','bluejeans',full_string)
    full_string = re.sub('bjn','bluejeans',full_string)
    full_string = re.sub('["]','',full_string)
    full_string = re.sub('[-]',' ',full_string)
    full_string = re.sub('[@]','at',full_string)
    full_string = re.sub('[...]','',full_string)
    full_string = re.sub('[!#?)+=$(%~^*]','',full_string)
    full_string = re.sub('[&]','and',full_string)
    full_string = re.sub('[\']','',full_string)
    full_string = re.sub('[;]','',full_string)
    full_string = re.sub('[,]','',full_string)
    full_string = re.sub('[.]','',full_string)
    full_string = re.sub('[/]',' ',full_string)
    full_string = re.sub('[\\\\]',' ',full_string)
    full_string= re.sub('plug-in','plugin',full_string)
    full_string = re.sub('[0123456789]','',full_string)
    ctr.update(full_string.split())
    
    
    
    
    cleaned = []  
    
    items = zip(coms,data)
    print "Cleaning comments"
    for item in items:
        words = item[0]
        words = words.decode('ascii','ignore')
        words = words.lower()
        words = re.sub('sound','audio',words)
        words = re.sub('bj','bluejeans',words)
        words = re.sub('bjn','bluejeans',words)
        words = re.sub('["]','',words)
        words = re.sub('[-]',' ',words)
        words = re.sub('[@]','at',words)
        words = re.sub('[...]','',words)
        words = re.sub('[!#?)+=$(%~^*]','',words)
        words = re.sub('[&]','and',words)
        words = re.sub('[\']','',words)
        words = re.sub('[,]','',words)
        words = re.sub('[.]','',words)
        words = re.sub('[;]','',words)
        words = re.sub('[/]',' ',words)
        words= re.sub('plug-in','plugin',words)
        words = re.sub('[0123456789]','',words)
        #wnl.lemmatize(word)
        temp = [word for word in words.split() if word not in \
        stopwords and ctr[word] >= min_count and len(word)>2]
          
        if temp != "" and temp !=" " and temp != [] and len(temp)>=min_length:
            words = ' '.join(temp)
            stamps = item[1]
            stamps.insert(0,words)
            cleaned.append(stamps)
   
    print 'Returned %d clean comments' % len(cleaned)
    print "SAMPLE COMMENT",cleaned[0]
    return cleaned


    
    
def store_file(cleaned,outfile):
    '''
    Writes a csvfile for further use, key designates name
    The file is written to ~/Desktop/key.txt
    '''
    outfile = open(outfile,'w')
    writer = csv.writer(outfile, delimiter=',')
    
    for line in cleaned:          
        writer.writerow(line)
    outfile.close()
    
    print 'stored csv to %s' % outfile
        
def store_mallet_file(cleaned,outfile):
    '''
    Writes text file of just comments in the proper form for MALLET
    The file is written to ~/mallet/key.txt
    '''

    outfile = open(outfile, 'w')
    writer = csv.writer(outfile, delimiter=',')
    for line in cleaned:
        writer.writerow(['NUll ','NULL ', line[0]])
        
    outfile.close()
    print 'Stored MALLET compatible file of comments to %s'% outfile
    

def main():

            
  
    cleaned = clean_text_multiple(coms,other_data)
    store_file(cleaned,outfilekey=key)
         
    
    
    
if __name__=='__main__':
    main()   

   
    
    
    
                              
    
    
