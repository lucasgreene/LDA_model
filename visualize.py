#!/usr/bin/env python

import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from datetime import datetime
date_format = '%Y-%m-%d'
time_format = '%Y-%m-%dT%H:%M:%S.000Z'
import pandas as pd
import os
import csv



 
def round_odd(num):
    if num%2==0:
        odd = num-1
    else:    
        if np.floor(num)%2==0:
            odd = np.ceil(num)
        else:
            odd = np.floor(num)
    return int(odd)
def assert_times(days):
    test = []
    for i in range(len(days)-1):
        if days[i] <= days[i+1]:
            pass
        else:
            test.append(i)
    assert test == []    
def parse(data):
    topics = data['topics'].values
    timestamps = data['timestamp'].values
    times = []
    timestring = []
    for i in range(len(topics)):
        topics[i] = np.array([float(weight) for weight in topics[i].split(',')])
        timestring.append(timestamps[i])
        time = datetime.strptime(timestamps[i][:10], date_format)
        times.append(datetime.strptime(timestamps[i],time_format))
        timestamps[i] = time
    data['timestamp'], data['topics'], data['times'] = timestamps, topics, times
    data['timestring'] = timestring
    return data
       
class simple_average(object):
    '''
    This class computes the triple simple moving average with decreasing windows
    The only parameter is the window size. A good number is around 13. Window must 
    be odd. 
    Simple moving averages create a delay in the signal equal to half of the size of 
    the window -1. Due to the iterations, there are actually 3 lags. A window of 13
    creates a lag of about 15 days. The scale on the graph is shifted to account for this,
    so the dates should be accurate. That is why the last two weeks do not appear on 
    the graph.
    '''
    
    def __init__(self, days, window):            
        self.unique_days = sorted(set(days))
        self.days = np.array(days)
        self.window = window
        
    
    def compute_av_counts(self, docs):    
        '''
        Compues a simple moving average with 3 iterations. The window size decreases
        by ~ 1.2 to cancel the higher frequency inversion
        '''
        alpha = np.sum(docs)/np.sum(np.sum(docs))
        av_per_day = []
        responses_per_day = []
        for day in self.unique_days:
            ind = np.where(self.days==day)
            per_day = len(ind[0])
            av_per_day.append(np.sum(docs[ind],0)/per_day)
            responses_per_day.append(per_day)
        upper = self.window
        pass1 = []
        while upper <= len(av_per_day):
            temp = np.array(av_per_day[upper-self.window:upper])
            weight = np.array(responses_per_day[upper-self.window:upper])**0.5           
            for i in range(len(temp)):
                temp[i] = temp[i]*weight[i]                      
            count = np.sum(temp,0)/np.sum(weight)
            pass1.append(count)
            upper += 1     
        window2 = round_odd(self.window/1.21)
        upper = window2
        pass2 = []
        while upper <= len(pass1):
            temp = np.array(pass1[upper-window2:upper])                     
            count = np.sum(temp,0)/window2
            pass2.append(count)
            upper += 1      
        window3 = round_odd(window2/1.21)
        upper = window3
        pass3 = []
        while upper <= len(pass2):
            temp = np.array(pass1[upper-window3:upper])                     
            count = np.sum(temp,0)/window3
            pass3.append(count)
            upper += 1                        
            
        return np.array(pass3), [self.window,window2,window3], alpha
    
    def get_av_graphs(self, roll_avg, windows,alpha,store,path):
        '''
        Plots with a shifted time to account for lag
        The number of topics needs to be even for the subplots to work
        This is very easy to change manually
        '''
        lost_days = len(self.unique_days)-len(roll_avg)      
        upper_bound = -(lost_days/2)
        lower_bound = lost_days/2
        time_range = self.unique_days[lower_bound:upper_bound]
        num_topics = len(roll_avg[0])
        plt.figure(10)
        #Find the factors for the subplot
        if num_topics/4 == num_topics/4.:
            a = num_topics/4
            b = num_topics/a
        else:
            a = num_topics/2
            b = num_topics/a
        for topic_num in range(num_topics):
            fit = np.polyfit(np.arange(len(roll_avg)),roll_avg[:,topic_num],1)
            fit_fn = np.poly1d(fit)
            plt.subplot(b,a,topic_num+1)
            plt.plot(time_range, roll_avg[:,topic_num],'-')           
            plt.plot(time_range, fit_fn(np.arange(len(time_range))))
            plt.plot(time_range, np.ones(len(roll_avg))*alpha[topic_num])
            plt.title('Topic %s'% topic_num)            
        plt.subplots_adjust(left=0.07, bottom=0.07, right=0.95, top=0.90, hspace = 0.7)
        plt.suptitle('Simple Moving Average')
        if store:
            plt.savefig(path+'/graphs/topics_simple_av')
        else:
            plt.show()
     
        
class exp_average(object):    
    '''
    This class computes the exponential moving average of the topic proportions
    Parameters:
    -> window controls the number of responses in the time window. The time 
    series is non-homogenous so a window of 20 may be half a day, or a weekend, 
    depending on how many responses we received in that time
    -> smooth controls a multiplier in the smoothing parameter of the model
    Larger values give smoother distributions, but they increase lag
    This model should lag less than the simple moving model, but how much it lags 
    excatly is hard to tell. 
    '''
    
    
    def __init__(self, window, smooth):
          self.window = window
          self.smooth = smooth
    
    def compute_exp_counts(self,docs):    
        docs = np.array(docs) 
        alpha = np.sum(docs)/np.sum(np.sum(docs))
        window_range = self.window
        upper = window_range
        topic_num= len(docs[0]) 
        counts = []
        # First initialize with simple average
        temp = docs[upper-self.window:upper]
        new = np.sum(temp)/float(self.window)
        counts.append(new)
        upper += 1   
        i = 0
        while upper < len(docs):
            temp = docs[upper]
            new = temp*self.smooth+counts[i]*(1-self.smooth)         
            counts.append(new)
            upper += 1
            i += 1
        return np.array(counts),alpha
        
    def get_exp_graphs(self,counts,alpha,times,store,path):
        plt.figure(1)
        loss = len(times)-len(counts)
        time_range = times[loss:]
        time_range = time_range.astype(datetime)
        x_range = np.arange(len(time_range))
        num_topics = len(counts[0])
        #Find the factors for the subplot
        if num_topics/4 == num_topics/4.:
            a = num_topics/4
            b = num_topics/a
        else:
            a = num_topics/2
            b = num_topics/a
        for i in range(num_topics):     
            avg = alpha[i]
            fit = np.polyfit(x_range,counts[:,i],1)
            fit_fn = np.poly1d(fit)
            plt.subplot(b,a,i+1)
            plt.plot(time_range,counts[:,i])
            plt.plot(time_range, [avg]*len(x_range), time_range, fit_fn(x_range))
            plt.title(str(i))
        plt.subplots_adjust(left=0.07, bottom=0.07, right=0.95, top=0.90, hspace = 0.7)
        plt.suptitle('Exponential Moving Average')    
        if store:
            plt.savefig(path+'/graphs/topics_exp_av')
        else:
            plt.show()
class compare(object):
    def __init__(self):
        pass
    def compute_proportions(self, docs, subset):
        print len(docs),len(subset)
        totalSums = np.zeros(len(docs[0]))
        sums = np.zeros(len(subset[0]))            
        for doc in docs:
            totalSums += doc
        for doc in subset:
            sums += doc
               
        print totalSums,sums
        totalSums = totalSums/np.sum(totalSums)
        sums = sums/np.sum(sums)
        proportions = sums/totalSums
        return proportions
    
    def get_avg_charts(self, proportions, field, item):
        x = len(proportions)
        plt.figure(5)
        plt.bar(np.arange(x), proportions)
        plt.plot(np.arange(x+1), [1]*(x+1))
        plt.axis([0,x,0,2])
        plt.xticks(np.arange(x)+0.4,(np.arange(x)))
        plt.title('%s = %s vs total proportions'% (field,item))
        plt.xlabel('Topic Num')
        plt.ylabel('Proportions')
        plt.show()
    
    def compute_counts(self, docs1, docs2):
        docs1, docs2 = np.array(docs1), np.array(docs2)
        print "Comaring %d and %d entries"%  (docs1.shape[0],docs2.shape[0])
        counts1 = np.zeros(len(docs1[0]))
        counts2 = np.zeros(len(docs2[0]))
        for doc in docs1:
            counts1 += doc
        for doc in docs2:
            counts2 += doc
        counts1, counts2 = counts1/np.sum(counts1), counts2/np.sum(counts2)
        return counts1, counts2  
    
    def get_compared_bars(self, counts1, counts2, item1, item2):
        x = np.arange(len(counts1))
        plt.figure(6)
        width=0.35
        plt.title('%s and %s Compared by freqency of topics'% (item1,item2))
        plt.bar(x, counts1, width, color='b')
        plt.bar(x+width, counts2, width, color='r')
        plt.legend(('%s'% item1,'%s'% item2), loc=2)
        plt.ylabel('Frequency')
        plt.xlabel('Topics')
        plt.xticks(x+width, x)
        plt.show()          

def main():
    '''
    Uses a csv saved as qualaroo_csv.txt in topics/texts
    '''
    
    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--field', dest='field', help='The field you want to query')                                                        
    p.add_option('--items', dest='item', help='Item of field for query')
    p.add_option('--show-output','-s', dest='show_output', action='store_true', 
                                 default=False, help='If true displays queried') 
    p.add_option('--simple-av', dest='SA', action='store_true', 
                help='''Triple-iteration simple moving average, window must be ODD''')
    p.add_option('--exp-av', dest='EA', action='store_true', 
                 help='''Exponential moving average''')
    p.add_option('--window', default=1, type='int', 
       help='''Parameter for moving averages, specifies number of days (simple)
             or number of individual time stamps (exponential) ''')
    p.add_option('--smooth', type='float', default=0.0015, 
                help='''Smoothing parameter in exponential average''')                                                                                                                    
    p.add_option('--count','-c', default=False, action='store_true', 
                                                help='Count collection')                                                 
    p.add_option('--show-one', dest='show_one', default=False, action='store_true',
                 help='Set to true to see example')
    p.add_option('--compare-avg', dest='compare_avg', action='store_true', 
                 help='''If true will create bar charts to show difference between 
                         query and total, i.e enterprise vs. total average''')
    p.add_option('--compare', action='store_true', help='Compares two items in field')
    p.add_option('--regex', 
                 help='Use this in place of --item for regex matching, overrides item')
    p.add_option('--show-most', dest='SM', 
                 help='Shows top 10 of whatever field is provided')
    p.add_option('--store', default=False, action='store_true', help='Saves graphs')
    (options, args) = p.parse_args()
    
    path = os.path.abspath('..')
    csv_file = path+'/texts/qualaroo_csv.txt'
    data = parse(pd.read_csv(csv_file))
 
     
    if options.regex:
        import re 
        item = re.compile("^%s"% options.regex, re.IGNORECASE)
  
    if options.item and options.field:
        selection = data[data[options.field] == options.item]
    else:
        selection = data  

    #Drop the begining of January, lack of responses   
    selection = selection[selection['times'] > datetime(2014,2,5,0,0)]
    selection = selection.sort(['times'])
         
    if options.show_one:
        print selection[:1]
        print selection.colums.values
    if options.count:
        print len(selection)
    
    docs, days = selection['topics'].values, selection['timestamp'].values      
    assert_times(days)
    
    if options.SM:
       print selection[options.SM].value_counts()[:20]
                       
    if options.SA:
        SA = simple_average(days, window=options.window)
        roll_avg, windows, alpha = SA.compute_av_counts(docs)
        time_range = SA.get_av_graphs(roll_avg, windows, alpha,options.store,path)
    if options.EA:
        times = selection['timestring'].values
        for i in range(len(times)):
            times[i] = datetime.strptime(times[i],time_format)
        _,ind = np.unique(times, return_index=True)
        docs,times = docs[ind],times[ind]
        assert_times(times)
        EA = exp_average(window=200, smooth=options.smooth)
        exp_counts,alpha = EA.compute_exp_counts(docs)   
        EA.get_exp_graphs(exp_counts,alpha,times,options.store,path)
    
    if options.compare_avg:
        subset = data[data[args[0]] == args[1]]['topics'].values
        CMP = compare()
        proportions = CMP.compute_proportions(subset,docs)
        CMP.get_avg_charts(proportions, options.field, options.item)
    
    if options.compare: 
        selection1 = data[data[options.field] == args[0]]
        selection2 = data[data[options.field] == args[1]]
        docs1 = selection1['topics'].values
        docs2 = selection2['topics'].values
        CMP = compare()
        counts1, counts2 = CMP.compute_counts(docs1, docs2)        
        CMP.get_compared_bars(counts1, counts2, item1=args[0], item2=args[1])
        
           
if __name__ == '__main__':
    main()
    
    
 
        
    
    
    
    
    
    
    
    
