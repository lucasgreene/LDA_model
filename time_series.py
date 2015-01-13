#!/usr/bin/env python
import numpy as np
import csv
from matplotlib import pyplot as plt
from datetime import datetime
date_format = '%Y-%m-%d'
time_format = '%Y-%m-%dT%H:%M:%S.000Z'
import os


def simple(scores,days,title,ylabel):
    unique = []
    nums = []
    av = []
    for day in sorted(set(days)):
         num = len(np.where(days==day)[0])
         nums.append(num)
         unique.append(day)     
         av.append(np.sum(scores[np.where(days==day)])/float(num))
    
    #Triple Pass Averaging    
    w1 = []
    window = 13
    upper =  window
    while upper<=len(av):
        temp = np.array(av[upper-window:upper])
        weight = np.array(nums[upper-window:upper])**(1./2)
        alpha = np.sum(temp*weight)/float(sum(weight))
        w1.append(alpha)
        upper += 1

    w2 = []
    window = 11
    upper = window
    while upper<=len(w1):
        w2.append(sum(w1[upper-window:upper])/float(window))
        upper += 1

    w3 = []
    window = 9
    upper = window
    while upper<=len(w2):
        w3.append(sum(w2[upper-window:upper])/float(window))
        upper += 1
    
    plot_title = 'Simple Moving Average (by day) \n' + title
    lag = len(unique)-len(w3)
    date_range = unique[lag/2:-lag/2]
    plt.plot(date_range,w3)
    plt.title(plot_title)
    plt.ylabel(ylabel)


def exp(scores, times, smooth, title,ylabel):
    # EXPONENTIAL MOVING AVERAGE
    # Remove all non-unique times
    _,un = np.unique(times,return_index=True)
    new_scores = scores[un]
    new_times = times[un]
    
    w2 = []
    window = 100
    upper = window
    temp = np.array(new_scores[upper-window:upper])
    alpha = np.sum(temp)/float(window)
    w2.append(alpha)
    upper += 1
    i = 0
    while upper<len(new_scores):
        temp = new_scores[upper]
        alpha = temp*smooth+w2[i]*(1-smooth)
        w2.append(alpha)
        upper += 1
        i += 1
    
    plot_title = 'Exponential Moving Average \n' + title
    lag = len(new_times)-len(w2)
    date_range = new_times[lag:]
    plt.plot(date_range,w2)
    plt.title(plot_title)
    plt.ylabel(ylabel)



def main():
    
    path = os.path.abspath('..')
    File =  open(path+'/texts/scores.txt')
    reader = csv.reader(File, delimiter=',')
    scores = []
    platform = []
    days = []
    times = []
    for line in reader:
        scores.append(int(line[3]))
        platform.append(line[1])
        days.append(datetime.strptime(line[0][:10],date_format))
        times.append(datetime.strptime(line[0],time_format))
    File.close()
    times = np.array(times)
    scores = np.array(scores)
    days = np.array(days)
    frame = np.where(days>datetime(2014,2,5,0,0))
    days = days[frame]
    scores = scores[frame]
    times = times[frame]

    ind = np.argsort(times)
    days = days[ind]
    scores = scores[ind]
    times = times[ind]

    '''Simple moving average, 3 iterations, windows=[13,11,9]
                 2 LEVELS [0,1] = [Okay/Good/Great,Poor/Bad]
                 The proportion of Poor/Bad Calls'''
    
    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--bad',action='store_true', help=''' If true will graph the 
                    proportion of Bad/Poor calls instead of the average score''')
    p.add_option('--smooth', type='float', default=0.0001, help='Parameter for exp')
    p.add_option('--store', action='store_true', help='If true saves the graphs')
    (options,args) = p.parse_args()
    
    if options.bad:
        ind1 = np.where(scores == 1)
        ind2 = np.where(scores == 2)
        ind3 = np.where(scores == 3)
        ind4 = np.where(scores == 4)
        ind5 = np.where(scores == 5)        
        scores[ind1] = 1
        scores[ind2] = 1
        scores[ind3] = 0
        scores[ind4] = 0
        scores[ind5] = 0
        plt.figure(1)
        title = 'Proportion of scores that are Bad/Poor'
        key = 'prop_bad_'
        ylabel = 'Proportion of total'
        plt.subplot(2,1,1)
        simple(scores,days,title,ylabel)
        plt.subplot(2,1,2)
        exp(scores,times,options.smooth,title,ylabel)
        
    else:
        title = 'Average Score'
        key = 'avg_'
        ylabel = 'Average Q-score'
        plt.figure(1)
        plt.subplot(2,1,1)
        simple(scores,days,title,ylabel)
        plt.subplot(2,1,2)
        exp(scores,times,options.smooth,title,ylabel)
    
    plt.subplots_adjust(hspace = 0.5)    
    if options.store:
        plt.savefig(path+'/graphs/%sscores.png'% key)
    else:
        plt.show()
if __name__ == '__main__':
    main()




