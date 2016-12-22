# -*- coding: utf-8 -*-
'''
 NAME:                ReportPlots.py

 DESCRIPTION:         Tools for parsing and plotting log file info

 EXECUTION COMMAND:   function call
 INPUTS:              As called functions
 OUTPUTS:             As defined in function

 NOTES:               change the input data. 
                      change the output PDF name.
                      
 AUTHOR:              Jon Hayenga
                      VisionGate Inc. 
 REVISION HISTORY:
                      Written/collected into this form -jwh 9-16-2015
                      Finally made to work - jwh 10-16-2015
                      
'''
import numpy as np
import matplotlib as mpl
#import matplotlib.backends.backend_pdf as cnv
mpl.use('Qt4Agg')
from matplotlib.dates import DateFormatter, HourLocator
import matplotlib.dates as dates
import matplotlib.pyplot as plt
import re
import time
mpl.interactive(True)

mrkrs = [ 'r.', 'b.', 'g.','m.','c.','y.','k.',\
          'ro', 'bo', 'go','mo','co','yo','ko',\
          'rv', 'bv', 'gv','mv','cv','yv','kv',\
          'rs', 'bs', 'gs','ms','cs','ys','ks',\
          'rp', 'bp', 'gp','mp','cp','yp','kp',\
          'rh', 'bh', 'gh','mh','ch','yh','kh',\
          ]
plotcolors = ['r','b','g','m','c','y','k']

def PlotAndSaveStatHistTimes(timelist,datalist,bc,CCT_name,plotname,dataunits,status_condition,condition_counts,plotspathSummary):
    '''----------------------------------------------------
    Plot[1] group data 
    Stats, histogram + time plot
    --------------------------------------------------------''' 
    formattime = ' Done {0:>6.4f} seconds \n'    
    tic0 = time.time() 
    print('- Plotting ',bc,plotname)
    fig1 = stats_hist_time_plot(timelist,datalist,bc,CCT_name,plotname,'Counts')
    toc0 = (time.time() - tic0)
    print('Barcode: ',bc)
    print(formattime.format(toc0))
    print()              
    PDFPathPlusName = plotspathSummary+'\\BC-'+str(bc)+'-'+plotname+'-'+CCT_name+'.png'
    try:
        plt.savefig(PDFPathPlusName,bbox='tight')
    except RuntimeError:
        print('No Plot -SaveFig error')
    plt.close()
    return fig1
#------------------------------------------------------------------------------------
'''---------------------------------------------------
TruncateList - chops Data list Time series received as text data 
and returns time date or float for plotting.
Tests for float and eliminates other options type conversion try
Uses only the first (leftmost) data in any one yseries data point
Assumes all data is space delimited (as it should be)
Expects only one data in xseries data point
Eliminates time data point for any nan or -1 entry.
Returns two lists, tlist and dlist.  
X is presumed but does not have to be a timedate series.
'''
def TruncateList(xseries,yseries):
    tlist=[]
    dlist=[]
    rflag = 1; newval=0.0
    for jj,val in enumerate(yseries):
        if str(val)=='nan':
            continue
        if (' ' in str(val)):
            wordy =re.split(' ',str(val))
            if wordy[0] == ' ':
                wordz = wordy[1]
            else:
                wordz=wordy[0]
        else:
            wordz = val
        try:
            newval = float(wordz)
        except:
            rflag=0
        if rflag==1:
            tlist.append(xseries[jj])
            dlist.append(newval)
        rflag=1
    return tlist, dlist



def splitTimeLists(timelist, datalist,slopeObjCount):
    ''' Receive a timelist and associated datalist and split into 24 hour date list pairs
    return a list of indexes at day boundaries and a list of rates (derivative of datalist) 
    filtered with a 15 sample kernel.
'''
    seconds_delay=[]

    kernel = np.ones(slopeObjCount)/slopeObjCount
    # find all the 24 hour boundaries
    day_index=[]
    for tc,ts in enumerate(timelist): #count the days that data covers and calculate data rate
        if tc>0: # wait til counter passes first data point for differential calculation
            if not(ts.day==timelist[tc-1].day):  # if the day isn't the same as last data point save the index
                day_index.append(tc-1)
            seconds_delaytemp = (ts - timelist[tc-1]).total_seconds()
            seconds_delay.append(seconds_delaytemp)
        else:
            seconds_delay.append(10)
    seconds_delay_averaged = np.convolve(seconds_delay,kernel, mode='same')
    objperhour = 3600/seconds_delay_averaged
    day_index.append(len(timelist)-1) ; # Add last data point index
#    print()
#    for tc, dl in enumerate(seconds_delay):
#        print(tc,ratelist0[tc],dl,seconds_delay_averaged[tc])
    return day_index, objperhour

'''
Produce a statistics report on datalist as top subplot
Produce a count of timestamps in a scatter plot in second subplot space

status_condition =['','ok','did_not_rotate','object_out_of_frame_left','object_out_of_frame_right', \
        'object_out_of_frame_top','object_out_of_frame_bottum','object_out_of_focus','object_not_in_first_image',\
        'feature_extraction_failed','segmentation_failed','unable_to_calc_object_width']
'''
def rate_stats_plot(timelist,datalist,bc,CCT_name,plotname,dataunits,objcount,status_condition,condition_counts):   
    slopeObjCount = 30 #number of object times averaged to use to measure slope of datalist
    strt_datetime = min(timelist)
    end_datetime = max(timelist)
    bc = int(bc)
    format1 = '| {0:<30} | {1:^20} | {2:^10} \n'
    format2 = '| {0:<30} | {1:>20,d} | {2:>6.2f} \n'
    format3 = '| {0:<30} | {1:>20,d} |\n'
    format4 = '  {0:<20}  {1:>20} \n'
    fmt1 = '%H:%M:%S'
    s0 = format4.format(('Barcode: '+str(bc)),  ('Instr: '+CCT_name))
    s0 = s0+ '\n'
    s0 = s0+ format1.format('Item', 'Value', 'Percent')
    s0 = s0+ '===========================================================================\n'
    s0 = s0+ format3.format((plotname+' Count Total '),  objcount)
    for cc, cond in enumerate(status_condition):
        if cond =='':
            cond = 'No Status (blank)'
        s0 = s0+ format2.format(status_condition[cc],   condition_counts[cc],      condition_counts[cc]/objcount*100)
    s0 = s0+ format4.format('Start Date/Time :',     str(strt_datetime))
    s0 = s0+ format4.format('End   Date/Time :',     str(end_datetime ))
    object_accumulation=[]
    for tt, tsl in enumerate(timelist):
        object_accumulation.append(tt+1)  
    # Some calculation as to how many plots to make
    timeIndexes, ratelist = splitTimeLists(timelist, datalist,slopeObjCount)
    '''----------------------------------------------------
    Plot[0] 
    Throughput figure and object count stats
    --------------------------------------------------------''' 
    # total hack fudge because Matplot lib doesn't handle time ranges correctly 
    #producing rediculous numbers of tics that abort the plot so a bogus date of 2001,1,1 
    #is chosen to use for plotting datetime instead of time ughhh
    begRange = dates.datetime.datetime(2001,1,1,0,0,0)
    endRange = dates.datetime.datetime(2001,1,1,23,59,59)
    figname0=('BarCode-'+str(bc)+' '+plotname+'-Object Counts')
    fig0 = plt.figure(figname0)   
    fig0.set_size_inches(10, 8, forward=True, dpi=300)
    ax01 = fig0.add_subplot(3,1,1)
    plt.text(0.05, 0.7,s0,horizontalalignment='left', verticalalignment='center',\
             fontweight='normal',fontsize=8,family='monospace')  
    ax01.axis('off')
    #-----------------------------------------------------
    y2range = max(object_accumulation)
    y2range -= (y2range % +100)
    y3range =1500
    xaxisArange=[begRange, endRange]  # plot within a 24 hour range
    ax02A = fig0.add_subplot(3,1,2)
    ax02A.set_title(('Barcode: '+str(bc)+plotname+' vs Time'), fontsize = 10)
    legendlist =[]
    for tc,ti in enumerate(timeIndexes):
        if tc ==0:
            timelist1 =timelist[0:(ti-1)]
            objAccum1 = object_accumulation[0:(ti-1)]
        elif tc==(len(timeIndexes)-1):
            timelist1 =timelist[timeIndexes[(tc-1)]:-1]
            objAccum1 = object_accumulation[timeIndexes[(tc-1)]:-1]
        else:
            timelist1 =timelist[timeIndexes[tc-1]:(ti-1)]
            objAccum1 = object_accumulation[timeIndexes[tc-1]:(ti-1)]
        legendlist.append(timelist.date[ti-1])
        print(tc,ti)
        timelist1_normalized_to_same_date = []
        for dtl in timelist1:
            timelist1_normalized_to_same_date.append(dates.datetime.datetime.combine(begRange.date(),dtl.time()))
        ax02A.plot(timelist1_normalized_to_same_date,objAccum1,mrkrs[tc], markersize = 5, fillstyle = 'none')
    ax02A.set_ylabel('Object Count', fontsize=8)
    ax02A.xaxis.set_major_locator(HourLocator())
    xfmt = DateFormatter(fmt1)
    ax02A.xaxis.set_major_formatter(xfmt)
    ax02A.grid('on',axis='both') 
    ax02A.minorticks_on
    ax02A.set_ylim([0,y2range])
    ax02A.set_xlim(xaxisArange)
    ax02A.set_xticklabels([])  # hide the axis in first plot
    plt.legend(legendlist, loc=2, prop={'size':8})
    mpl.rcParams['ytick.labelsize'] = 8
    #plt.setp(plt.getp(plt.getp(ax02A,'axes'), 'yticklabels'), fontsize=8)
    #plt.setp(ax02A.get_xticklabels(), visible=False)
    #-----------------------------------------------------------------
    #ax03A = plt.subplot2grid((6,12),(4,0), colspan=12, rowspan=2)
    ax03A = plt.subplot(3,1,3)
    for tc,ti in enumerate(timeIndexes):
        if tc ==0:
            timelist2 =timelist[0:(ti-1)]
            rate1 = ratelist[0:(ti-1)]
        elif tc==(len(timeIndexes)-1):
            timelist2 =timelist[timeIndexes[(tc-1)]:-1]
            rate1 = ratelist[timeIndexes[(tc-1)]:-1]
        else:
            timelist2 =timelist[timeIndexes[tc-1]:(ti-1)]
            rate1 = ratelist[timeIndexes[tc-1]:(ti-1)]
        timelist3 = []
        for dtl in timelist2:
            timelist3.append(dates.datetime.datetime.combine(begRange.date(),dtl.time()))
        rop1 = int(slopeObjCount/2)
        rop2 = len(rate1)-int(slopeObjCount/2)
        if len(timelist3)>rop2:
            ax03A.plot(timelist3[rop1:rop2],rate1[rop1:rop2],mrkrs[tc], markersize = 5, fillstyle = 'none')
    ax03A.set_ylabel((plotname+' per Hour'), fontsize=10)
    ax03A.xaxis.set_major_locator(HourLocator(interval=1))
    xfmt = DateFormatter(fmt1)
    ax03A.xaxis.set_major_formatter(xfmt)
    ax03A.set_ylim([0,y3range])
    #if len(timelist1_normalized_to_same_date)> slopeObjCount:
    ax03A.set_xlim(xaxisArange)
    tmpplt = plt.getp(ax03A,'axes')
    plt.setp(plt.getp(tmpplt, 'yticklabels'), fontsize=8)
    plt.setp(plt.getp(tmpplt, 'xticklabels'), fontsize=8, rotation =90)
    ax03A.set_xlabel('Time', fontsize=10)
    ax03A.minorticks_on
    ax03A.grid('on',axis='both')
    fig0.subplots_adjust(hspace=0.1, wspace=0.1,bottom=0.175, top=0.9, left =0.06, right = 0.95)        
    plt.show()

        
    return fig0

#--------------------------------------------------------------------------------
'''
Produce a statistics report on datalist as top subplot
Produce a vertical histogram plot to left of time plot of same datalist
'''
def stats_hist_time_plot(timelist,datalist,bc,CCTname,plotname,dataunits,y1range):
    if y1range== 1 or y1range==2 or y1range==3:
        stdev =y1range #if its and int assume this stdev implied for limits +/- 1,2,or3 stdev from mean
        Item = np.nan_to_num(np.array(datalist))
        Itemmean = np.mean(Item[Item>0.0])
        Itemstd =  np.std(Item[Item>0.0])
        ymn = np.min(Item)
        if ymn<0:
            yrange = [Itemmean-stdev*Itemstd,Itemmean+stdev*Itemstd]
        else:
            yrange=[-.1,Itemmean+stdev*Itemstd]
    else:
        yrange=y1range
    print(yrange,y1range,plotname)
    begRange = dates.datetime.datetime(2001,1,1,0,0,0)
    endRange = dates.datetime.datetime(2001,1,1,23,59,59)
    fig1 = plt.figure(('BarCode-'+str(bc)+' '+plotname))
    fig1.set_size_inches(10, 8, forward=True, dpi=300)
    bc=int(bc)
    fmt = '%H:%M:%S'
    format4 = '  {0:<20}  {1:>20} \n'
    format5 = '| {0:<20}  {1:>6.2f} \n'
    dezerod = []
    for val in datalist:
        if val>0:
            dezerod.append(val)
    s1 = format4.format(('Barcode: '+str(bc)),  ('Instr: '+CCTname), plotname)
    s1=s1+ '\n'
    s1=s1+ format5.format(plotname+'Values Count ',float(len(dezerod)))        
    s1=s1+ format5.format(plotname+' Min       : ', np.min(dezerod))
    s1=s1+ format5.format(plotname+' Max       : ', np.max(dezerod))
    s1=s1+ format5.format(plotname+' Mean      : ',np.mean(dezerod))
    s1=s1+ format5.format(plotname+' StdDev    : ', np.std(dezerod))
    s1=s1+ format5.format(plotname+' % CoefVar : ', np.std(dezerod)/np.mean(dezerod)*100)
    s1=s1+ format5.format(plotname+' Median    : ', np.median(dezerod))
    s1=s1+ ' all zero underflows have been removed from stats calculations \n'

    ax11 = plt.subplot2grid((6,12),(0,0), colspan=12, rowspan=2) 
    plt.text(0.15, 0.7,s1,\
             horizontalalignment='left', verticalalignment='center',\
             fontweight='normal',fontsize=8,family='monospace')  
    ax11.axis('off')        
    #-----------------------------------------------------
#    bincount = int(np.max(datalist)-np.min(datalist))
#    if bincount > 500:
#        bincount = 500
    bincount =100
    try:
        hist1,histbins = np.histogram(datalist, range=([np.min(datalist),np.max(datalist)]),\
                         bins = bincount, weights=None, density=None, )
        bin_max =histbins[np.where(hist1 == hist1.max())]
        peak = bin_max[0]
        stdev = np.std(datalist)
        spanplus = peak+3*stdev
        spanminus = peak-3*stdev
        span = [spanminus,spanplus]
    except ValueError:
        s= "Value error in Hist"
        plt.text(.5,.5,s,fontsize = 8, family='monospace',verticalalignment='center',horizontalalignment='left')
        span = [min(datalist),max(datalist)] 
        
    if yrange ==[]:
        span = [min(datalist),max(datalist)] 
    else:
        span = yrange
    #-----------------------------------------------------
    ax12 = plt.subplot2grid((6,12),(2,0),colspan=3, rowspan=4)
    ax13 = plt.subplot2grid((6,12),(2,3),colspan=9, rowspan=4)
    ax13.set_title(plotname+' vs Time', fontsize = 9)
    timeIndexes, dummy = splitTimeLists(timelist, datalist,30)
    legendlist=[]
    for tc,ti in enumerate(timeIndexes):
        if tc ==0:
            timelist2 =timelist[0:(ti-1)]
            datalist2 = datalist[0:(ti-1)]
        elif tc==(len(timeIndexes)-1):
            timelist2 =timelist[timeIndexes[(tc-1)]:-1]
            datalist2 = datalist[timeIndexes[(tc-1)]:-1]
        else:
            timelist2 =timelist[timeIndexes[tc-1]:(ti-1)]
            datalist2 = datalist[timeIndexes[tc-1]:(ti-1)]
        timelist3 = []
        legendlist.append(timelist.date[ti-1])
        # shift all timelists to a common date to compensate for python bug
        for dtl in timelist2:
            timelist3.append(dates.datetime.datetime.combine(begRange.date(),dtl.time()))            
        try:
            ax12.hist(datalist2, range=(span),\
                    bins =bincount, \
                    weights=None, orientation='horizontal', color=plotcolors[tc], histtype='bar',rwidth=0.2, fill = True)
        except ValueError:
            print(bc, 'Value Error - problem with histogram data')
        ax13.plot(timelist3,datalist2,mrkrs[tc], markersize = 5, fillstyle = 'none')
    #-------------------------------------------------------------------
    plt.sca(ax12)    
    plt.xlabel('Count', fontsize=10)
    plt.ylabel(dataunits, fontsize=8)
    plt.ylim(span)
    plt.setp(plt.getp(plt.getp(ax12,'axes'), 'xticklabels'), fontsize=7)
    plt.setp(plt.getp(plt.getp(ax12,'axes'), 'xticklabels'), rotation =90)
    plt.setp(plt.getp(plt.getp(ax12,'axes'), 'yticklabels'), fontsize=9)
    plt.grid('on',axis='both')
    ax12.minorticks_on
    ax12.grid(b=True, which='minor', color='r', linestyle='--')
    ax12.grid(True, which='major')
    #-------------------------------------------------------
    plt.sca(ax13)
    xaxisArange=[begRange, endRange]  # plot within a 24 hour range
    plt.ylim(span)
    ax13.yaxis.set_visible(False)
    plt.xlabel('Time of Day', fontsize=10)
    plt.grid('on',axis='both')
    ax13.set_xlim(xaxisArange)
    ax13.xaxis.set_major_locator(dates.HourLocator(interval=1))
    ax13.xaxis.set_major_formatter(dates.DateFormatter(fmt))
    #plt.setp(plt.getp(plt.getp(ax13,'axes'), 'yticklabels'), fontsize=10)
    plt.setp(plt.getp(plt.getp(ax13,'axes'), 'xticklabels'), fontsize=7)
    plt.setp(plt.getp(plt.getp(ax13,'axes'), 'xticklabels'), rotation =90)
    #plt.setp(plt.getp(plt.getp(ax12,'axes'), 'yticklabels'), fontsize=1)
    ax13.minorticks_on
    plt.legend(legendlist, loc=3, prop={'size':8})
    plt.grid('on',axis='both')
    ax13.grid(b=True, which='minor', color='k', linestyle='--')
    ax13.grid(True, which='major')
    fig1.subplots_adjust(hspace=0.1, wspace=0.1,bottom=0.175, top=0.9, left =0.1, right = 0.9)  
    plt.show()
    return fig1


'''
Produce a statistics report on datalist as top subplot
Produce a vertical histogram plot to left of time plot of same datalist
'''
def stats_hist_time_plot2(timelist,datalist,datalistb,bc,CCTname,plotname,dataunits,y1range):
    if y1range== 1 or y1range==2 or y1range==3:
        stdev =y1range #if its and int assume this stdev implied for limits +/- 1,2,or3 stdev from mean
        Item = np.nan_to_num(np.array(datalist))
        Itemmean = np.mean(Item[Item>0.0])
        Itemstd =  np.std(Item[Item>0.0])
        yrange = [Itemmean-stdev*Itemstd,Itemmean+stdev*Itemstd]
    else:
        yrange=y1range
    begRange = dates.datetime.datetime(2001,1,1,0,0,0)
    endRange = dates.datetime.datetime(2001,1,1,23,59,59)
    fig1 = plt.figure(('BarCode-'+str(bc)+' '+plotname))
    fig1.set_size_inches(10, 8, forward=True, dpi=300)
    bc=int(bc)
    fmt = '%H:%M:%S'
    format4 = '  {0:<20}  {1:>20} \n'
    format5 = '| {0:<20}  {1:>6.2f} \n'
    
    s1 = format4.format(('Barcode: '+str(bc)),  ('Instr: '+CCTname), plotname)
    s1=s1+ '\n'
    s1=s1+ format5.format(plotname+'Values Count ',float(len(datalist)))        
    s1=s1+ format5.format(plotname+' Min       : ', np.min(datalist))
    s1=s1+ format5.format(plotname+' Max       : ', np.max(datalist))
    s1=s1+ format5.format(plotname+' Mean      : ',np.mean(datalist))
    s1=s1+ format5.format(plotname+' StdDev    : ', np.std(datalist))
    s1=s1+ format5.format(plotname+' % CoefVar : ', np.std(datalist)/np.mean(datalist)*100)
    s1=s1+ format5.format(plotname+' Median    : ', np.median(datalist))
    s1=s1+'\n'

    ax11 = plt.subplot2grid((6,12),(0,0), colspan=12, rowspan=2) 
    plt.text(0.15, 0.7,s1,\
             horizontalalignment='left', verticalalignment='center',\
             fontweight='normal',fontsize=8,family='monospace')  
    ax11.axis('off')        
    #-----------------------------------------------------
    bincount = int(np.max(datalist)-np.min(datalist))
    if bincount > 500:
        bincount = 500
    try:
        hist1,histbins = np.histogram(datalist, range=([np.min(datalist),np.max(datalist)]),\
                         bins = bincount, weights=None, density=None, )
        bin_max =histbins[np.where(hist1 == hist1.max())]
        peak = bin_max[0]
        stdev = np.std(datalist)
        spanplus = peak+3*stdev
        spanminus = peak-3*stdev
        span = [spanminus,spanplus]
    except ValueError:
        s= "Value error in Hist"
        plt.text(.5,.5,s,fontsize = 8, family='monospace',verticalalignment='center',horizontalalignment='left')
        span = [min(datalist),max(datalist)] 
        
    if yrange ==[]:
        span = [min(datalist),max(datalist)] 
    else:
        span = yrange
    #-----------------------------------------------------
    ax12 = plt.subplot2grid((6,12),(2,0),colspan=3, rowspan=4)
    ax13 = plt.subplot2grid((6,12),(2,3),colspan=9, rowspan=4)
    ax13.set_title(plotname+' vs Time', fontsize = 9)
    timeIndexes, dummy = splitTimeLists(timelist, datalist,30)
    legendlist=[]
    for tc,ti in enumerate(timeIndexes):
        if tc ==0:
            timelist2 =timelist[0:(ti-1)]
            datalist2 = datalist[0:(ti-1)]
            datalistb2= datalistb[0:(ti-1)]
        elif tc==(len(timeIndexes)-1):
            timelist2 =timelist[timeIndexes[(tc-1)]:-1]
            datalist2 = datalist[timeIndexes[(tc-1)]:-1]
            datalistb2 = datalistb[timeIndexes[(tc-1)]:-1]
        else:
            timelist2 =timelist[timeIndexes[tc-1]:(ti-1)]
            datalist2 = datalist[timeIndexes[tc-1]:(ti-1)]
            datalistb2 = datalistb[timeIndexes[tc-1]:(ti-1)]
        timelist3 = []
        legendlist.append(timelist.date[ti-1])
        # shift all timelists to a common date to compensate for python bug
        for dtl in timelist2:
            timelist3.append(dates.datetime.datetime.combine(begRange.date(),dtl.time()))            
        try:
            ax12.hist(datalist2, range=(span),\
                    bins =bincount, \
                    weights=None, orientation='horizontal', color=plotcolors[tc], histtype='bar',rwidth=0.2, fill = True)
        except ValueError:
            print(bc, 'Value Error - problem with histogram data')
        avgdata = (np.array(datalist2) + np.array(datalistb2))/2
        errdata = (np.abs(np.array(datalist2) - np.array(datalistb2)))/2
        ax13.errorbar(timelist3, avgdata, yerr=errdata, fmt=mrkrs[tc], ms=4)
        
    #-------------------------------------------------------------------
    #Set axist labelling properties for plots
    plt.sca(ax12)    
    plt.xlabel('Count', fontsize=10)
    plt.ylabel(dataunits, fontsize=8)
    plt.ylim(span)
    plt.setp(plt.getp(plt.getp(ax12,'axes'), 'xticklabels'), fontsize=7)
    plt.setp(plt.getp(plt.getp(ax12,'axes'), 'xticklabels'), rotation =90)
    plt.setp(plt.getp(plt.getp(ax12,'axes'), 'yticklabels'), fontsize=9)
    plt.grid('on',axis='both')
    ax12.minorticks_on
    ax12.grid(b=True, which='major', color='r', linestyle='--')
    ax12.grid(True, which='major')
    #-------------------------------------------------------
    plt.sca(ax13)
    xaxisArange=[begRange, endRange]  # plot span of data to spread out error bars as much as possible
    plt.ylim(span)
    ax13.yaxis.set_visible(False)
    plt.xlabel('Time of Day', fontsize=10)
    plt.grid('on',axis='both')
    ax13.set_xlim(xaxisArange)
    ax13.xaxis.set_major_locator(dates.HourLocator(interval=1))
    ax13.xaxis.set_major_formatter(dates.DateFormatter(fmt))
    #plt.setp(plt.getp(plt.getp(ax13,'axes'), 'yticklabels'), fontsize=10)
    plt.setp(plt.getp(plt.getp(ax13,'axes'), 'xticklabels'), fontsize=7)
    plt.setp(plt.getp(plt.getp(ax13,'axes'), 'xticklabels'), rotation =90)
    plt.setp(plt.getp(plt.getp(ax13,'axes'), 'yticklabels'), fontsize=4)
    plt.grid('on',axis='bot')
    ax13.minorticks_on
    plt.legend(legendlist, loc=3, prop={'size':8})
    ax13.grid(b=True, which='major', color='r', linestyle='--')
    ax13.grid(True, which='major')
    fig1.subplots_adjust(hspace=0.1, wspace=0.1,bottom=0.175, top=0.9, left =0.1, right = 0.9) 
    plt.show()
        
    return fig1


'''
Produce an array in 3D plot of stop velocities versus time.

'''
def Stoptime_plot3D(timelist,ylist,zlist,bc,CCTname,plotname,dataunits,yrange,zrange):

    begRange = dates.datetime.datetime(2001,1,1,0,0,0)
    endRange = dates.datetime.datetime(2001,1,1,23,59,59)
    fig1 = plt.figure(('BarCode-'+str(bc)+' '+plotname))
    fig1.set_size_inches(10, 8, forward=True, dpi=300)
    bc=int(bc)
    fmt = '%H:%M:%S'
    format4 = '  {0:<20}  {1:>20} \n'
    format5 = '| {0:<20}  {1:>6.2f} \n'
    
    s1 = format4.format(('Barcode: '+str(bc)),  ('Instr: '+CCTname), plotname)
    s1=s1+ '\n'
    s1=s1+ format5.format(plotname+'Values Count ',float(len(ylist)))        
    s1=s1+ format5.format(plotname+' Min       : ', np.min(ylist))
    s1=s1+ format5.format(plotname+' Max       : ', np.max(ylist))
    s1=s1+ format5.format(plotname+' Mean      : ',np.mean(ylist))
    s1=s1+ format5.format(plotname+' StdDev    : ', np.std(ylist))
    s1=s1+ format5.format(plotname+' % CoefVar : ', np.std(ylist)/np.mean(ylist)*100)
    s1=s1+ format5.format(plotname+' Median    : ', np.median(ylist))
    s1=s1+'\n'

    ax11 = plt.subplot2grid((6,12),(0,0), colspan=12, rowspan=2) 
    plt.text(0.15, 0.7,s1,\
             horizontalalignment='left', verticalalignment='center',\
             fontweight='normal',fontsize=8,family='monospace')  
    ax11.axis('off')        
    #-----------------------------------------------------
    bincount = int(np.max(ylist)-np.min(ylist))
    if bincount > 500:
        bincount = 500
    try:
        hist1,histbins = np.histogram(ylist, range=([np.min(ylist),np.max(ylist)]),\
                         bins = bincount, weights=None, density=None, )
        bin_max =histbins[np.where(hist1 == hist1.max())]
        peak = bin_max[0]
        stdev = np.std(ylist)
        spanplus = peak+3*stdev
        spanminus = peak-3*stdev
        span = [spanminus,spanplus]
    except ValueError:
        s= "Value error in Hist"
        plt.text(.5,.5,s,fontsize = 8, family='monospace',verticalalignment='center',horizontalalignment='left')
        span = [min(ylist),max(ylist)] 
        
    if yrange ==[]:
        span = [min(ylist),max(ylist)]
    else:
        span = yrange
    #-----------------------------------------------------
    ax12 = plt.subplot2grid((6,12),(2,0),colspan=3, rowspan=4)
    ax13 = plt.subplot2grid((6,12),(2,3),colspan=9, rowspan=4)
    ax13.set_title(plotname+' vs Time', fontsize = 9)
    timeIndexes, dummy = splitTimeLists(timelist, ylist,30)
    legendlist=[]
    for tc,ti in enumerate(timeIndexes):
        if tc ==0:
            timelist2 =timelist[0:(ti-1)]
            ylist2 = ylist[0:(ti-1)]
        elif tc==(len(timeIndexes)-1):
            timelist2 =timelist[timeIndexes[(tc-1)]:-1]
            ylist2 = ylist[timeIndexes[(tc-1)]:-1]
        else:
            timelist2 =timelist[timeIndexes[tc-1]:(ti-1)]
            ylist2 = ylist[timeIndexes[tc-1]:(ti-1)]
        timelist3 = []
        legendlist.append(timelist.date[ti-1])
        # shift all timelists to a common date to compensate for python bug
        for dtl in timelist2:
            timelist3.append(dates.datetime.datetime.combine(begRange.date(),dtl.time()))            
        try:
            ax12.hist(ylist2, range=(span),\
                    bins =bincount, \
                    weights=None, orientation='horizontal', color=plotcolors[tc], histtype='bar',rwidth=0.2, fill = True)
        except ValueError:
            print(bc, 'Value Error - problem with histogram data')
        ax13.plot(timelist3,ylist2,mrkrs[tc], markersize = 5, fillstyle = 'none')
    #-------------------------------------------------------------------
    plt.sca(ax12)    
    plt.xlabel('Count', fontsize=10)
    plt.ylabel(dataunits, fontsize=8)
    plt.ylim(span)
    plt.setp(plt.getp(plt.getp(ax12,'axes'), 'xticklabels'), fontsize=7)
    plt.setp(plt.getp(plt.getp(ax12,'axes'), 'xticklabels'), rotation =90)
    plt.setp(plt.getp(plt.getp(ax12,'axes'), 'yticklabels'), fontsize=9)
    plt.grid('on',axis='both')
    ax12.minorticks_on
    ax12.grid(b=True, which='minor', color='r', linestyle='--')
    ax12.grid(True, which='major')
    #-------------------------------------------------------
    plt.sca(ax13)
    xaxisArange=[begRange, endRange]  # plot within a 24 hour range
    plt.ylim(span)
    ax13.yaxis.set_visible(False)
    plt.xlabel('Time of Day', fontsize=10)
    plt.grid('on',axis='both')
    ax13.set_xlim(xaxisArange)
    ax13.xaxis.set_major_locator(dates.HourLocator(interval=1))
    ax13.xaxis.set_major_formatter(dates.DateFormatter(fmt))
    #plt.setp(plt.getp(plt.getp(ax13,'axes'), 'yticklabels'), fontsize=10)
    plt.setp(plt.getp(plt.getp(ax13,'axes'), 'xticklabels'), fontsize=7)
    plt.setp(plt.getp(plt.getp(ax13,'axes'), 'xticklabels'), rotation =90)
    ax13.minorticks_on
    plt.legend(legendlist, loc=3, prop={'size':8})
    plt.grid('on',axis='both')
    ax13.grid(b=True, which='minor', color='k', linestyle='--')
    ax13.grid(True, which='major')
    fig1.subplots_adjust(hspace=0.1, wspace=0.1,bottom=0.175, top=0.9, left =0.1, right = 0.9)  
    plt.show()
        
    return fig1


'''
Produce a statistics report on datalist as top subplot
Produce a vertical histogram plot to left of time plot of same datalist
'''
def stats_2D_plot(timelist,datalist,bc,CCTname,plotname,dataunits,y1range,horlabel):
    if y1range== 1 or y1range==2 or y1range==3:
        stdev =y1range #if its an int assume this stdev implied for limits +/- 1,2,or3 stdev from mean
        Item = np.nan_to_num(np.array(datalist))
        Itemmean = np.mean(Item[Item>0.0])
        Itemstd =  np.std(Item[Item>0.0])
        yrange = [Itemmean-stdev*Itemstd,Itemmean+stdev*Itemstd]
    else:
        yrange=y1range
    print(yrange,y1range,plotname)
    fig1 = plt.figure(('BarCode-'+str(bc)+' '+plotname))
    fig1.set_size_inches(10, 8, forward=True, dpi=300)
    bc=int(bc)
    #fmt = '%H:%M:%S'
    format4 = '  {0:<20}  {1:>20} \n'
    format5 = '| {0:<20}  {1:>6.2f} \n'
    
    s1 = format4.format(('Barcode: '+str(bc)),  ('Instr: '+CCTname), plotname)
    s1=s1+ '\n'
    s1=s1+ format5.format(plotname+'Values Count ',float(len(datalist)))        
    s1=s1+ format5.format(plotname+' Min       : ', np.min(datalist))
    s1=s1+ format5.format(plotname+' Max       : ', np.max(datalist))
    s1=s1+ format5.format(plotname+' Mean      : ',np.mean(datalist))
    s1=s1+ format5.format(plotname+' StdDev    : ', np.std(datalist))
    s1=s1+ format5.format(plotname+' % CoefVar : ', np.std(datalist)/np.mean(datalist)*100)
    s1=s1+ format5.format(plotname+' Median    : ', np.median(datalist))
    s1=s1+'\n'

    ax11 = plt.subplot2grid((6,12),(0,0), colspan=12, rowspan=1) 
    plt.text(0.15, 0.7,s1,\
             horizontalalignment='left', verticalalignment='center',\
             fontweight='normal',fontsize=8,family='monospace')  
    ax11.axis('off')        
    #-----------------------------------------------------

    ax13 = plt.subplot2grid((6,12),(2,1),colspan=11, rowspan=5)
    ax13.set_title(plotname+horlabel, fontsize = 9)
    m,b=np.polyfit(timelist,datalist,1)
    ax13.plot(timelist,datalist,'b.', markersize = 2, fillstyle = 'none')
    plt.sca(ax13)
    plt.ylim(yrange)
    ax13.yaxis.set_visible(True)
    plt.ylabel(dataunits, fontsize=10)
    plt.xlabel('Seconds from start', fontsize=10)
    plt.grid('on',axis='both')
    plt.setp(plt.getp(plt.getp(ax13,'axes'), 'yticklabels'), fontsize=10)
    plt.setp(plt.getp(plt.getp(ax13,'axes'), 'xticklabels'), fontsize=7)
    plt.setp(plt.getp(plt.getp(ax13,'axes'), 'xticklabels'), rotation =90)
    
    ax13.minorticks_on
    msg = '    '+str(m)+'-slope   '+str(b)+'-offset'
    plt.text(0,(.9*(yrange[1]-yrange[0])+yrange[0]),msg)
    plt.grid('on',axis='both')
    ax13.grid(b=True, which='minor', color='k', linestyle='--')
    ax13.grid(True, which='major')
    fig1.subplots_adjust(hspace=0.1, wspace=0.1,bottom=0.175, top=0.9, left =0.1, right = 0.9)  
    plt.show()
    return fig1
'''
Produce a statistics report on datalist as top subplot
Produce a vertical histogram plot to left of time plot of same datalist
'''
def Dual_2D_plot(timelist,datalist,datalist2,bc,CCTname,plotname1,plotname2,dataunits,y1range,horlabel):
    if y1range== 1 or y1range==2 or y1range==3:
        stdev =y1range #if its an int assume this stdev implied for limits +/- 1,2,or3 stdev from mean
        Item = np.nan_to_num(np.array(datalist))
        Itemmean = np.mean(Item[Item>0.0])
        Itemstd =  np.std(Item[Item>0.0])
        yrange = [Itemmean-stdev*Itemstd,Itemmean+stdev*Itemstd]
    else:
        yrange=y1range
    print(yrange,y1range,plotname1)
    fig1 = plt.figure(('BarCode-'+str(bc)+' '+plotname1))
    fig1.set_size_inches(10, 8, forward=True, dpi=300)
    bc=int(bc)
    #fmt = '%H:%M:%S'
    format4 = '  {0:<20}  {1:>20} \n'
    format5 = '| {0:<20}  {1:>6.2f} \n'
    
    s1 = format4.format(('Barcode: '+str(bc)),  ('Instr: '+CCTname), plotname1)
    s1=s1+ '\n'
    s1=s1+ format5.format(plotname1+'Values Count ',float(len(datalist)))        
    s1=s1+ format5.format(plotname1+' Min       : ', np.min(datalist))
    s1=s1+ format5.format(plotname1+' Max       : ', np.max(datalist))
    s1=s1+ format5.format(plotname1+' Mean      : ',np.mean(datalist))
    s1=s1+ format5.format(plotname1+' StdDev    : ', np.std(datalist))
    s1=s1+ format5.format(plotname1+' % CoefVar : ', np.std(datalist)/np.mean(datalist)*100)
    s1=s1+ format5.format(plotname1+' Median    : ', np.median(datalist))
    s1=s1+'\n'

    ax11 = plt.subplot2grid((6,12),(0,0), colspan=12, rowspan=1) 
    plt.text(0.15, 0.7,s1,\
             horizontalalignment='left', verticalalignment='center',\
             fontweight='normal',fontsize=8,family='monospace')  
    ax11.axis('off')        
    #-----------------------------------------------------

    ax13 = plt.subplot2grid((6,12),(2,1),colspan=11, rowspan=5)
    ax13.set_title(plotname1+horlabel, fontsize = 9)
    m,b=np.polyfit(timelist,datalist,1)
    ax13.plot(timelist,datalist,'b.', markersize = 4, fillstyle = 'none')
    ax13.plot(timelist,datalist2,'r.',markersize=2, fillstyle='full')
    plt.sca(ax13)
    plt.ylim(yrange)
    ax13.yaxis.set_visible(True)
    plt.ylabel(dataunits, fontsize=10)
    plt.xlabel('Seconds from start', fontsize=10)
    plt.grid('on',axis='both')
    plt.setp(plt.getp(plt.getp(ax13,'axes'), 'yticklabels'), fontsize=10)
    plt.setp(plt.getp(plt.getp(ax13,'axes'), 'xticklabels'), fontsize=7)
    plt.setp(plt.getp(plt.getp(ax13,'axes'), 'xticklabels'), rotation =90)
    plt.legend([plotname1,plotname2], loc=3, prop={'size':8})
    ax13.minorticks_on
    msg = '    '+str(m)+'-slope   '+str(b)+'-offset'
    plt.text(0,(.9*(yrange[1]-yrange[0])+yrange[0]),msg)
    plt.grid('on',axis='both')
    ax13.grid(b=True, which='minor', color='k', linestyle='--')
    ax13.grid(True, which='major')
    fig1.subplots_adjust(hspace=0.1, wspace=0.1,bottom=0.175, top=0.9, left =0.1, right = 0.9) 
    plt.show()
    return fig1