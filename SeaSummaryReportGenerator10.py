"""
PhxSummaryReportGenerator_R1

Reads the LogData_Rx.CSV listed for plotting data.
Data is read into Python scripts (Pandas dataframe) for plotting.
Summary includes:
- Time to process by barcode, rate of objects per hour, rate of successful 3D per hour
- Count of restarts for barcode
- Lamp_Setting vs time, and histogram, stats (min, max, avg, stdev, median)
- Stop_Time_delta vs time, and histogram, stats (min, max, avg, stdev, median)
- ObjXMin & ObjXMax vs time, and histogram, stats (min, max, avg, stdev, median)
- Cap_Z_Center & Cap_Y_Center & C3D_CapCenter_Y & C3D_CapCenter_Z 
                    vs time, and histogram, stats (min, max, avg, stdev, median)
- Radius vs time, and histogram, stats (min, max, avg, stdev, median)
- Obj_Radius vs time, and histogram, stats (min, max, avg, stdev, median)
- Time_To_Stop vs time, and histogram, stats (min, max, avg, stdev, median)

valueKeys['File_Dir']=['',0]
valueKeys['CCT_Name']=['',0]
valueKeys['File_Time']=['',0]
valueKeys['Restart']=['spe ',4]
valueKeys['Timeout']=['Fifteen',2]
valueKeys['Note']=['NOTEID',3]
valueKeys['Bar_Code']=[':BarCode,',11]
valueKeys['Sample_Type']=['specimencategory=',1]
valueKeys['WaferClass']=[':3dd',5]
valueKeys['WaferStatus']=['',5]
valueKeys['WaferID']=['',5]
valueKeys['Version']=[':Perforce Changelist: ',0]
valueKeys['Lamp_Setting']=['LampSetting,',0]
valueKeys['Pressure_Time_delta']= [':Time to pressure ,',0]
valueKeys['Stop_DeltaT']=[':Time to stop ,',0] # from setup tracking to longitudinal motor stop
valueKeys['Obj_Found_TS']=[':Setup Tracking',6]
valueKeys['StopFlow_TS']=[':Time to stop ,',6]
valueKeys['ObjXMin']=[':Min AbsX During Rotation,',0]
valueKeys['ObjXMax']=[':Max AbsX During Rotation,',0]
valueKeys['Cap_Z_Center']=[':Focus Centroid,',0] # units = microns
valueKeys['Cap_Y_Center']= [':Y Centroid,',0] # units = microns
valueKeys['Angle']=[':Angle,',0] # degrees
valueKeys['FlowRadius_rough']=[':Radius,',0] # microns
valueKeys['FlowRadius_refined']=['capradius=',8] #millimeters
valueKeys['Rot_Offset']=['rotationoffset=',0] # degrees
valueKeys['Obj_ID']=[':hpic3d send3dldt=true',9] # no units
valueKeys['C3D_Status']=[':c3d status=',10]
valueKeys['C3D_CapCenter_Y']=['',10] # microns
valueKeys['C3D_CapCenter_Z']=['',10] # microns
valueKeys['C3D_Msg']=['',10]
valueKeys['BarPressMF']=['MassFlowPressure=',7] # Read in PSI and recorded in Bar
valueKeys['RadMF']=['',7] # millimeters
valueKeys['ObjVel']=['',7] # millimeter per second
valueKeys['MFVel']=['',7] # millimeters per second
valueKeys['PkVel']=['',7] # millimeters per second
valueKeys['MassFlow']=['',7] # microliters per second
valueKeys['FlowResistance']=['',7] # ? atmospheres/mm^3/second
valueKeys['AmbientTemp']=[':rtmban nd,',12] # deg C
valueKeys['FPGAbd_Temp']=[':rtmmea pumpsi,',12] # deg C
valueKeys['Illuminator_Temp']=['temperature=',0] # deg C
valueKeys['Objective_Waveform']=['focusvolt=',3] # volts
valueKeys['Obj_Area']=['',10]
valueKeys['Obj_PosIndx']=['',10]
valueKeys['Obj_AbsV']=['',10]
valueKeys['Obj_FrameID']=['',10]
valueKeys['Obj_Rot']=['',10]
valueKeys['Obj_FS']=['',10]
valueKeys['StopDeltaT']=[':imo ',13]
valueKeys['StopVel']=['',13]
valueKeys['Pump_StartTime']=[':Start Pump',14] # time pump commanded to pressureize
valueKeys['Idle_dt']=['STATE DELTA TIME,Idle',15] # Recorded Stack Time (previous data set)
valueKeys['Stack_dt']=['STATE DELTA TIME,Stack',15] # Recorded Stack Time (previous data set)
valueKeys['Search_dt']=['STATE DELTA TIME,Search',15] # Record all the Search times in log comma delimited
valueKeys['Search_dt_cnt'] = ['',15]
valueKeys['Track_dt']=['STATE DELTA TIME,Track',15] # Tracking/stopping time find all the lines with this key word and comma delimit in a
valueKeys['Track_dt_cnt'] = ['',15]                   # in a single text entry into a cell.
valueKeys['3DCal_dt']=['STATE DELTA TIME,3D Cal',15]
valueKeys['3DCal_dt_cnt'] = ['',15]
valueKeys['PP_dt']=['STATE DELTA TIME,PP',15]
valueKeys['PumpMoveRequest']=['rtmmot pum mov',16] 
valueKeys['PumpMoveResponse']=['rtmnotify pum',17]
valueKeys['PumpStrPot']=['rtmmea pummm',18] # must find the first rtmmea after line with 'rtmmea pummm'
valueKeys['PumpPressure1']=[' psi',19] # time stamp and psi reading as tuple
valueKeys['AdjustedPressure']=['Adjusted Pressure,',20] # time stamp and psi reading as tuple

jwh 8/12/15.
"""

import matplotlib as mpl
mpl.use('Qt4Agg')
import pandas as pd
import os
import re
import datetime as dt
import time
import numpy as np
import matplotlib.pyplot as plt
import ReportPlots_R10 as rp
mpl.interactive(True)
#import matplotlib.backends.backend_pdf as cnv
#from matplotlib.dates import DateFormatter, HourLocator
#import matplotlib.dates as dates
def AddUpAttempts(val1):
    val1=str(val1)
    ItemAttemptCount=0
    wordlist1= re.split(' ',val1)
    Itemtime = 0
    for word in wordlist1:
        if (word == '' or word=='nan' or word== 'NaN'):
            continue
        ItemAttemptCount +=1
        Itemtime += np.float(word)
    return ItemAttemptCount, Itemtime

FunctName = 'SeaSummaryReportGenerator'
FunctInfo= '''
SeaSummaryReportGenerator - creates graphical output from the LogData_RC.csv files and displays and
writes pdfs to a given path directory in LogData_Rx.csv. This is intended for development and data analysis work
typically oriented toward Seattle Testing of CCTs, but may be used anywhere.
'''
mrkrs = [ 'r.', 'b.', 'g.','m.','c.','y.','k.',\
          'ro', 'bo', 'go','mo','co','yo','ko',\
          'rv', 'bv', 'gv','mv','cv','yv','kv',\
          'rs', 'bs', 'gs','ms','cs','ys','ks',\
          'rp', 'bp', 'gp','mp','cp','yp','kp',\
          'rh', 'bh', 'gh','mh','ch','yh','kh',\
          ]
plotcolors = ['r','b','g','m','c','y','k']

delimx = ','
fmt = '%H:%M:%S.%f' # hour:minutes:seconds.decimalSeconds
fmt1 = '%y-%m-%d %H:%M:%S' # yy-mm-dd hours:min:sec"
fmt2 = '%y-%m-%d %H:%M:%S.%f' #yy-mm-dd hours:min:sec.decimalSeconds"
pth1 = input('Enter path to LogData_R- file: ')

#pth1 = 'U:\\DailyInstrumentData\\cct031\\gservlog\\ucm_logs\\cct031_201507' # testing file
SavedFileName = 'LogData_RC.csv'

PathPlusName = pth1+'\\'+SavedFileName  #path and name of data file
Data3 = pd.read_csv(PathPlusName, low_memory=False) # read all the data back into the variables for processing
TestRow = len(Data3)-1

#Data3[['Bar_Code']]=Data3[['Bar_Code']]
Data3.sort(columns=['Bar_Code']).astype(str)
Data3.set_index(keys=['Bar_Code'],drop=False,inplace=True)

ListofAllBarCodes = Data3.Bar_Code.unique().tolist()
tp = []
for i in ListofAllBarCodes:
    try:
        temp = int(i)
        tp.append(temp)
    except:
        continue
ListofAllBarCodes=tp
ListofAllBarCodes.sort()

Data3 = Data3.reset_index(drop=True) # make sure the index is reset

# Enable this code for interactive barcode selection & change ListofAllBarcodes to ListofBarCodes in for loop
ListofAllBarCodesAndStartTimes=[]
for bc in ListofAllBarCodes:
    BarcodeStartTime = min(pd.to_datetime(Data3.File_Time[Data3.Bar_Code == float(bc)].tolist()))
    ListofAllBarCodesAndStartTimes.append([BarcodeStartTime,bc])

ListofAllBarCodesAndStartTimes.sort(key=lambda tup: tup[0])

print("Enter Bar Codes to Plot: ")
print('----------+----------------------------')
print(' Bar Code   Bar Code Start Data/Time')
for bc in ListofAllBarCodesAndStartTimes:
    print(' ',int(bc[1]), '       ',bc[0])
print('  ')

StrofBarCodes = input('Enter bracketed comma delimmited list of Bar Codes to plot ',)
ListofStrofBarCodes = re.split(delimx,StrofBarCodes)
ListofBarCodes=[]
if StrofBarCodes=='':
    ListofBarCodes=ListofAllBarCodes
else:  #numbers come from input
    for bc in ListofStrofBarCodes:
        tmpbc = int(float(bc))
        ListofBarCodes.append(tmpbc)  # list of barcodes input parsed from string

'''Things to be plotted:
Summary of Rates,Lamp_Settings,Stop_Time, ObjX Positions,Capillary Center,
Object Radius, Object_Size,Stopping Times, Search Times

Read in the data with above headers from LogData_R**.csv '''
plotnames =['Total Objects','Lamp_Settings','Stop_Time', 'ObjX Positions','Capillary Center','Object Radius', 'Object_Size','Stopping Times']
plotspath = pth1+'\\Plots'
if not os.path.exists(plotspath):
    os.makedirs(plotspath)
plotspathSummary = plotspath+'\\Summary_V4Systems'
if not os.path.exists(plotspathSummary):
   os.makedirs(plotspathSummary)

CCTname = Data3.CCT_Name[1] # Which CCT is this?
MinObjects = 100 # must be this many objects in data set to follow through on plot

for bc in ListofBarCodes:
    bc = int(bc)
    bcQualify = [(Data3.Bar_Code== float(bc))]
    objcount   = pd.to_datetime(Data3.File_Time[    (Data3.Bar_Code== float(bc))]).count()
    if bc > 0 and objcount > MinObjects:
        OTs = pd.to_datetime(Data3.File_Time[       (Data3.Bar_Code== float(bc))].tolist()).order()
        WTs = pd.to_datetime(Data3.File_Time[       (Data3.Bar_Code== float(bc)) \
                                           & (Data3.WaferClass.astype(str)=='wafer')].tolist()).order()
        FileDateTime =     Data3.File_Time[         (Data3.Bar_Code== float(bc))].tolist()
        LampSettings =     Data3.Lamp_Setting[      (Data3.Bar_Code== float(bc))].tolist()
        StopTimes =        Data3.Stop_DeltaT[       (Data3.Bar_Code== float(bc))].tolist()
        ObjXMins =         Data3.ObjXMin[           (Data3.Bar_Code== float(bc))].tolist()
        ObjXMaxs =         Data3.ObjXMax[           (Data3.Bar_Code== float(bc))].tolist()
        Cap_Z_Centers =    Data3.Cap_Z_Center[      (Data3.Bar_Code== float(bc))].tolist()
        C3D_CapCenter_Zs = Data3.C3D_CapCenter_Z[   (Data3.Bar_Code== float(bc))].tolist()
        Cap_Y_Centers =    Data3.Cap_Y_Center[      (Data3.Bar_Code== float(bc))].tolist()
        C3D_CapCenter_Ys = Data3.C3D_CapCenter_Y[   (Data3.Bar_Code== float(bc))].tolist()
        Radii =            Data3.FlowRadius_refined[(Data3.Bar_Code== float(bc))].tolist()
        Obj_Radii =        Data3.FlowRadius_rough[  (Data3.Bar_Code== float(bc))].tolist()
        st = min(pd.to_datetime(Data3.File_Time[    (Data3.Bar_Code== float(bc))].tolist()))
        FlowResistance=    Data3.FlowResistance[    (Data3.Bar_Code== float(bc))].tolist()
        MassFlow=          Data3.MassFlow[          (Data3.Bar_Code== float(bc))].tolist()
        BarPressure=       Data3.BarPressMF[        (Data3.Bar_Code== float(bc))].tolist()
        MFVel=             Data3.MFVel[             (Data3.Bar_Code== float(bc))].tolist()
        FPGA_T=            Data3.FPGAbd_Temp[       (Data3.Bar_Code== float(bc))].tolist()
        Amb_T=             Data3.AmbientTemp[       (Data3.Bar_Code== float(bc))].tolist()
        Illum_T=           Data3.Illuminator_Temp[  (Data3.Bar_Code== float(bc))].tolist()
        #ObjWave=           Data3.Objective_Waveform[bcQualify].tolist()         
#        Obj_Area=          Data3.Obj_Area[bcQualify].tolist()   
#        Obj_PosIndx=       Data3.Obj_PosIndx[bcQualify].tolist()  
#        Obj_AbsV=          Data3.Obj_AbsV[bcQualify].tolist()  
#        Obj_FrameID=       Data3.Obj_FrameID[bcQualify].tolist()  
#        Obj_Rot=           Data3.Obj_Rot[(Data3.Bar_Code.astype(int)== bc)].tolist()  
#        Obj_FS=            Data3.Obj_FS[(Data3.Bar_Code.astype(int)== bc)].tolist()  
#        StopDeltaT=        Data3.StopDeltaT[(Data3.Bar_Code.astype(int)== bc)].tolist()  
#        StopVel=           Data3.StopVel[(Data3.Bar_Code.astype(int)== bc)].tolist()  
#        Pump_StartTime=    Data3.Pump_StartTime[(Data3.Bar_Code.astype(int)== bc)].tolist()  
        Idle_dt=           Data3.Idle_dt[(Data3.Bar_Code== float(bc))].tolist() 
        Idle_dt_cnt=       Data3.Idle_dt_cnt[(Data3.Bar_Code== float(bc))].tolist() 
        Search_dt=         Data3.Search_dt[(Data3.Bar_Code== float(bc))].tolist()  
        Search_dt_cnt=     Data3.Search_dt_cnt[(Data3.Bar_Code== float(bc))].tolist()
        D3Cal_dt=          Data3.D3Cal_dt[(Data3.Bar_Code== float(bc))].tolist()  
        D3Cal_dt_cnt=      Data3.D3Cal_dt_cnt[(Data3.Bar_Code== float(bc))].tolist()
        Stack_dt=          Data3.Stack_dt[(Data3.Bar_Code== float(bc))].tolist()
        Stack_dt_cnt=      Data3.Stack_dt_cnt[(Data3.Bar_Code== float(bc))].tolist()        
        Track_dt=          Data3.Track_dt[(Data3.Bar_Code== float(bc))].tolist() 
        Track_dt_cnt=      Data3.Track_dt_cnt[(Data3.Bar_Code== float(bc))].tolist()
        PP_dt=             Data3.PP_dt[(Data3.Bar_Code== float(bc))].tolist()
        PP_dt_cnt=         Data3.PP_dt_cnt[(Data3.Bar_Code== float(bc))].tolist()
        PumpMoveRequest=   Data3.PumpMoveRequest[ (Data3.Bar_Code== float(bc))].tolist() 
        PumpMoveResponse=  Data3.PumpMoveResponse[(Data3.Bar_Code== float(bc))].tolist() 
        PumpStrPot=        Data3.PumpStrPot[      (Data3.Bar_Code== float(bc))].tolist() 
        PumpPressure1=     Data3.PumpPressure1[   (Data3.Bar_Code== float(bc))].tolist() 
        AdjustedPressure=  Data3.AdjustedPressure[(Data3.Bar_Code== float(bc))].tolist() 
      
        BarcodeStartTime = st.strftime('%Y%m%d%H%M%S')

        '''----------------------------------------------------
        Plot[0] OTs data plus derived rate (derivative +lowpass averagin filter) data
        Throughput figure and object count status stats
        --------------------------------------------------------''' 
        formattime = ' Done {0:>6.4f} seconds \n'
        tic0 = time.time() 
        print(' Plotting ',bc,plotnames[0])
        status_conditions=['','ok','did_not_rotate','object_out_of_frame_left','object_out_of_frame_right', \
        'object_out_of_frame_top','object_out_of_frame_bottum','object_out_of_focus','object_not_in_first_image',\
        'feature_extraction_failed','segmentation_failed','unable_to_calc_object_width']
        condition_counts =[]
        for cc, cond in enumerate(status_conditions):
            cctot = pd.to_datetime(Data3.File_Time[(Data3.Bar_Code == float(bc)) & (Data3.WaferStatus.astype(str) ==status_conditions[cc])]).count()
            print('condition counts',cc,cctot)          
            condition_counts.append(cctot)
        #def rate_stats_plot(timelist,datalist,bc,CCT_name,plotname,dataunits,objcount,status_condition,condition_counts):   
        fig0 = rp.rate_stats_plot(OTs,OTs,bc,CCTname,plotnames[0],'Counts',objcount,status_conditions,condition_counts)
        toc0 = (time.time() - tic0)
        print('Barcode: ',bc)
        print(formattime.format(toc0))
        print()        
        pdffilename = pth1+'\\'+('Barcode-'+str(bc)+'-Graphs.pdf')        
        PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+' '+plotnames[0]+' '+CCTname+'.png'
        try:
            plt.savefig(PDFPathPlusName,bbox='tight')
        except RuntimeError:
            print('No Plot -SaveFig error')

        if len(WTs)>40:
            '''----------------------------------------------------
            Plot[0.5] WTs data plus derived rate (derivative +lowpass averagin filter) data
            Throughput figure and object count status stats
            --------------------------------------------------------''' 
            formattime = ' Done {0:>6.4f} seconds \n'
            tic0 = time.time() 
            objcount = len(WTs)
            print(' Plotting ',bc,'Wafers')
            status_conditions=['','ok','did_not_rotate','object_out_of_frame_left','object_out_of_frame_right', \
            'object_out_of_frame_top','object_out_of_frame_bottum','object_out_of_focus','object_not_in_first_image',\
            'feature_extraction_failed','segmentation_failed','unable_to_calc_object_width']   
            condition_counts =[]
            for cc, cond in enumerate(status_conditions):
                cctot = pd.to_datetime(Data3.File_Time[(Data3.Bar_Code == float(bc)) & \
                                                       (Data3.WaferStatus.astype(str) ==status_conditions[cc]) &\
                                                       (Data3.WaferClass.astype(str)== 'wafer')]).count()
                print('wafer condition counts',cc,cctot)          
                condition_counts.append(cctot)
            #def rate_stats_plot(timelist,datalist,bc,CCT_name,plotname,dataunits,objcount,status_condition,condition_counts):   
            fig05 = rp.rate_stats_plot(WTs,WTs,bc,CCTname,'Wafers','Counts',objcount,status_conditions,condition_counts)
            toc0 = (time.time() - tic0)
            print('Wafer Barcode: ',bc)
            print(formattime.format(toc0))
            print()        
            pdffilename = pth1+'\\'+('Barcode_'+str(bc)+'_Graphs.pdf')        
            PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+' '+'Wafers'+' '+CCTname+'.png'
            try:
                plt.savefig(PDFPathPlusName,bbox='tight')
            except RuntimeError:
                print('No Plot -SaveFig error')
        '''----------------------------------------------------
        Plot[1] LampSettings data 
        Stats, histogram + time plot
        --------------------------------------------------------''' 
        tic0 = time.time() 
        plotname = plotnames[1]
        data2plot = np.nan_to_num(np.array(LampSettings))  # condition the data removing any NANs or inf
        print(' Plotting ',bc,plotname)
        ymean = np.mean(data2plot)
        yrange = [ymean-250,ymean+250]
        fig1 = rp.stats_hist_time_plot(OTs,data2plot,bc,CCTname,plotname,'Counts',yrange)
        toc0 = (time.time() - tic0)
        print(formattime.format(toc0))
        print()               
        PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+' '+plotname+' '+CCTname+'.png'
        try:
            plt.savefig(PDFPathPlusName,bbox='tight')
        except RuntimeError:
            print('No Plot -SaveFig error')

        
        '''----------------------------------------------------
        Plot[2] StopTimes data 
        Stats, histogram + time plot
        --------------------------------------------------------''' 
        tic0 = time.time()
        plotname = plotnames[2]
        ST2plot = np.nan_to_num(np.array(StopTimes))
        print(' Plotting ',bc,plotname)
        yrange = [0, 3000]   
        fig2 = rp.stats_hist_time_plot(OTs,ST2plot,bc,CCTname,plotname,'milliseconds',yrange)
        toc0 = (time.time() - tic0)
        print(formattime.format(toc0))
        print()              
        PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+' '+plotname+' '+CCTname+'.png'
        try:
            plt.savefig(PDFPathPlusName,bbox='tight')
        except RuntimeError:
            print('No Plot -SaveFig error')

    
              
        '''----------------------------------------------------
        Plot[3] Longitudinal difference data 
        Stats, histogram + time plot
        --------------------------------------------------------''' 
        tic0 = time.time()
        plotname = 'Obj Longitude Translation'
        print(' Plotting ',bc,plotname)
        ObjTranslation = np.nan_to_num(np.array(ObjXMaxs))
        ObjTranslationb = np.array(ObjXMins)
        ymx=np.mean(ObjTranslation[ObjTranslation>0.0])
        yrange = [ymx-500,ymx+500] # range of plot is +/-500 microns from average
        fig3 = rp.stats_hist_time_plot2(OTs,ObjTranslation,ObjTranslationb,bc,CCTname,plotname,'microns',yrange)
        toc0 = (time.time() - tic0)
        print(formattime.format(toc0))
        print()              
        PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+' '+plotname+' '+CCTname+'.png'
        try:
            plt.savefig(PDFPathPlusName,bbox='tight')
        except RuntimeError:
            print('No Plot -SaveFig error')      
        

        '''----------------------------------------------------
        Plot[4] Flow Characteristics 
        Flow Resistance, MassFlow, PeakFlow, MassFlow Radius, ObjVelocity? 
        Histogram and stats for sample
        --------------------------------------------------------''' 
        tic0 = time.time()
        plotname = ' Flow Resistance'
        print(' Plotting ',bc,plotname)
        FlowR = np.nan_to_num(np.array(FlowResistance))
        yrange = 2
        fig4 = rp.stats_hist_time_plot(OTs,FlowR,bc,CCTname,plotname,'Atmosphere*Sec/uL',yrange)
        toc0 = (time.time() - tic0)
        print(formattime.format(toc0))
        print()              
        PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+' '+plotname+' '+CCTname+'.png'
        try:
            plt.savefig(PDFPathPlusName,bbox='tight')
        except RuntimeError:
            print('No Plot -SaveFig error')

        '''----------------------------------------------------
        Plot[4.2] Pressure Characteristics 
        Histogram and stats for sample
        --------------------------------------------------------''' 
        tic0 = time.time()
        plotname = 'PSI Pressure'
        print('-Plotting ',bc,plotname)
        PSItemp = np.array(BarPressure)*14.3
        PSIP = np.nan_to_num(PSItemp)
        yrange =[0,4000]
        fig4p2 = rp.stats_hist_time_plot(OTs,PSIP,bc,CCTname,plotname,'PSI',yrange)
        toc0 = (time.time() - tic0)
        print(formattime.format(toc0))
        print()              
        PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+' '+plotname+' '+CCTname+'.png'
        try:
            plt.savefig(PDFPathPlusName,bbox='tight')
        except RuntimeError:
            print('No Plot -SaveFig error')

        '''----------------------------------------------------
        Plot[4.3] Flow Characteristics 
        Flow Resistance, Pressure, MassFlow, MFlowVelocity? 
        Histogram and stats for sample
        --------------------------------------------------------''' 
        tic0 = time.time()
        plotname = 'Mass Flow Velocity'
        print('-Plotting ',bc,plotname)
        MFVelo = np.nan_to_num(np.array(MFVel))*1000
        yrange = [0,1500]
        fig4p3 = rp.stats_hist_time_plot(OTs,MFVelo,bc,CCTname,plotname,'um/Sec',yrange)
        toc0 = (time.time() - tic0)
        print(formattime.format(toc0))
        print()
        PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+' '+plotname+' '+CCTname+'.png'
        try:
            plt.savefig(PDFPathPlusName,bbox='tight')
        except RuntimeError:
            print('No Plot -SaveFig error')

        '''----------------------------------------------------
        Plot[5] Lateral-position data 
        Stats, histogram + time plot
        --------------------------------------------------------''' 
        tic0 = time.time()
        plotname = 'Lateral Position Delta'
        print('- Plotting ',bc,plotname)
        TimeData,Ycenter = rp.TruncateList(OTs,C3D_CapCenter_Ys)
        TimeSeries= pd.to_datetime(TimeData)
        yrange = 3
        fig5 = rp.stats_hist_time_plot(TimeSeries,Ycenter,bc,CCTname,plotname,'microns',yrange)
        toc0 = (time.time() - tic0)
        print(formattime.format(toc0))
        print()              
        PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+' '+plotname+' '+CCTname+'.png'
        try:
            plt.savefig(PDFPathPlusName,bbox='tight')
        except RuntimeError:
            print('No Plot -SaveFig error')


        '''----------------------------------------------------
        Plot[6] DistFromCenterFlow 
        Stats, histogram + time plot
        --------------------------------------------------------''' 
        tic0 = time.time()
        plotname = 'Flow Stream Radius'
        print('- Plotting ',bc,plotname)
        newR=[]
        newT=[]
        for jj, val in enumerate(Radii):
            temp = str(val)
            if not(temp =='nan' or val< 0.0):
                newR.append(val)
                newT.append(OTs[jj])
        TimeData,newRadii = rp.TruncateList(OTs,Radii)
        TimeSeries= pd.to_datetime(TimeData)
        RadiusDelta = np.array(newRadii)*1000
        yrange=[0,31]
        fig6 = rp.stats_hist_time_plot(TimeSeries,RadiusDelta,bc,CCTname,plotname,'microns',yrange)
        toc0 = (time.time() - tic0)
        print(formattime.format(toc0))
        print()              
        PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+' '+plotname+' '+CCTname+'.png'
        try:
            plt.savefig(PDFPathPlusName,bbox='tight')
        except RuntimeError:
            print('No Plot -SaveFig error')

        '''----------------------------------------------------
        Plot[8] Focus Position
        Focus position histogram + time plot
        --------------------------------------------------------''' 
        tic0 = time.time()
        plotname = 'Focus Position'
        print('- Plotting ',bc,plotname)
        TimeData,Zcenter = rp.TruncateList(OTs,C3D_CapCenter_Zs)
        TimeSeries= pd.to_datetime(TimeData)
        ObjFoc = np.array(Zcenter)
        yrange = 2
        fig8 = rp.stats_hist_time_plot(TimeSeries,ObjFoc,bc,CCTname,plotname,'microns',yrange)
        toc0 = (time.time() - tic0)
        print(formattime.format(toc0))
        print()              
        PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+' '+plotname+' '+CCTname+'.png'
        try:
            plt.savefig(PDFPathPlusName,bbox='tight')
        except RuntimeError:
            print('No Plot -SaveFig error')
        plt.close('all')
        
        '''----------------------------------------------------
        Plot[9] FPGATemperature
        Focus position histogram + time plot
        --------------------------------------------------------''' 
        tic0 = time.time()
        plotname = 'Temp FPGA'
        print('- Plotting ',bc,plotname)
        yrange=[20,200]
        fig9 = rp.stats_hist_time_plot(OTs,FPGA_T,bc,CCTname,plotname,'Deg C',yrange)
        toc0 = (time.time() - tic0)
        print(formattime.format(toc0))
        print()              
        PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+' '+plotname+' '+CCTname+'.png'
        try:
            plt.savefig(PDFPathPlusName,bbox='tight')
        except RuntimeError:
            print('No Plot -SaveFig error')
        plt.close('all')
        '''----------------------------------------------------
        Plot[10] AmbientTemperature
        Focus position histogram + time plot
        --------------------------------------------------------''' 
        tic0 = time.time()
        plotname = 'Temp Ambient'
        print('- Plotting ',bc,plotname)
        yrange=[10,40]
        fig10 = rp.stats_hist_time_plot(OTs,Amb_T,bc,CCTname,plotname,'Deg C',yrange)
        toc0 = (time.time() - tic0)
        print(formattime.format(toc0))
        print()              
        PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+' '+plotname+' '+CCTname+'.png'
        try:
            plt.savefig(PDFPathPlusName,bbox='tight')
        except RuntimeError:
            print('No Plot SaveFig error')
        plt.close('all')
        '''----------------------------------------------------
        Plot[10] Illuminator Temperature
        Focus position histogram + time plot
        --------------------------------------------------------''' 
        tic0 = time.time()
        plotname = 'Temp Illuminator'
        print('- Plotting ',bc,plotname)
        yrange=[10,60]
        fig10 = rp.stats_hist_time_plot(OTs,Illum_T,bc,CCTname,plotname,'Deg C',yrange)
        toc0 = (time.time() - tic0)
        print(formattime.format(toc0))
        print()              
        PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+' '+plotname+' '+CCTname+'.png'
        try:
            plt.savefig(PDFPathPlusName,bbox='tight')
        except RuntimeError:
            print('No Plot SaveFig error')
        plt.close('all')
        '''----------------------------------------------------
        Plot[11] Pump Absolute Position
        Pisition of pump over time.
        --------------------------------------------------------''' 
        tic0 = time.time()
        plotname = 'Pump Position Absolute'
        print('- Plotting ',bc,plotname)
        OTDateTime,PumpPosition = rp.TruncateList(OTs,PumpMoveResponse) 
        pAbsPos = np.array(PumpPosition)
        pAbsPosMicrons = pAbsPos.astype(np.float)
        pAbsPosMicrons = pAbsPosMicrons/25.0
        NewDT=pd.to_datetime(OTDateTime)
        Mintime = min(NewDT)
        DeltaSecs = []
        for jj, item in enumerate(NewDT):
            delta = (NewDT[jj]-Mintime).total_seconds()
            DeltaSecs.append(delta)
        ymin = 0.0
        ymax = 15000.0
        yrange=[ymin,ymax]
        horlabel='Time'
        fig10 = rp.stats_2D_plot(DeltaSecs,pAbsPosMicrons,bc,CCTname,plotname,'Pump Microns',yrange,horlabel)
        toc0 = (time.time() - tic0)
        print(formattime.format(toc0))
        print()              
        PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+' '+plotname+' '+CCTname+'.png'
        try:
            plt.savefig(PDFPathPlusName,bbox='tight')
        except RuntimeError:
            print('No Plot -SaveFig error')
        plt.close('all')
        '''----------------------------------------------------
        Plot[12] PumpRelative Position Accumulated
        Position of pump over time.
        --------------------------------------------------------''' 
#        tic0 = time.time()
#        plotname = 'Pump Position Incremental'
#        print('- Plotting ',bc,plotname)
#        OTDateTime,Ditem = rp.TruncateList(OTs,PumpMoveRequest) 
#        npDitem = np.array(Ditem)
#        NewDT2=pd.to_datetime(OTDateTime)
#        Mintime = min(NewDT2)
#        DeltaSecs = []
#        for jj, item in enumerate(NewDT2):
#            delta = (NewDT2[jj]-Mintime).total_seconds()
#            DeltaSecs.append(delta)
#        npfD =np.array(np.zeros(len(Ditem)))
#        for ii,npf in enumerate(npDitem):
#            try:
#                newf = np.float(npf)
#            except:
#                newf =0.0
#            if ii==0:
#                npfD[ii]=newf
#            else:
#                npfD[ii]=(newf+npfD[ii-1])
#        npscaled = np.array(npfD)/25.0 # convert to microns
#        ymin = np.min(npscaled)
#        ymax = np.max(npscaled)*1.1
#        yrange=[ymin,ymax]
#        horlabel='Time'
#        fig10 = rp.stats_2D_plot(DeltaSecs,npscaled,bc,CCTname,plotname,'Pump Microns',yrange,horlabel)
#        PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+' '+plotname+' '+CCTname+'.png'
#        try:
#            plt.savefig(PDFPathPlusName,bbox='tight')
#        except RuntimeError:
#            print('No Plot -SaveFig error')
#            plt.close('all')
#            toc0 = (time.time() - tic0)
#            print(formattime.format(toc0))
#            print() 
#        except:
#            print([str(bc)+plotname+' -Exception error - probably malformed time data'])
        '''----------------------------------------------------
        Plot[13] Pump StringPot Position
        Pisition of pump over time.
        --------------------------------------------------------''' 
        tic0 = time.time()
        plotname = 'Pump Position StringPot'
        print('- Plotting ',bc,plotname)
        OTDateTime,PumpPosition = rp.TruncateList(OTs,PumpStrPot) 
        pAbsPos = np.array(PumpPosition)
        pAbsPosMicrons = pAbsPos.astype(np.float)*1000 # convert to microns
        NewDT=pd.to_datetime(OTDateTime)
        Mintime = min(NewDT)
        DeltaSecs = []
        for jj, item in enumerate(NewDT):
            delta = (NewDT[jj]-Mintime).total_seconds()
            DeltaSecs.append(delta)
        ymin = 0.0
        ymax = np.max(pAbsPosMicrons)*1.1
        yrange=[ymin,ymax]
        horlabel='Time'
        fig10 = rp.stats_2D_plot(DeltaSecs,pAbsPosMicrons,bc,CCTname,plotname,'String Pump Pos in um',yrange,horlabel)
        toc0 = (time.time() - tic0)
        print(formattime.format(toc0))
        print()              
        PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+' '+plotname+' '+CCTname+'.png'
        try:
            plt.savefig(PDFPathPlusName,bbox='tight')
        except RuntimeError:
            print('No Plot -SaveFig error')
        plt.close('all')
      
        '''----------------------------------------------------
        Plot[14] Pump Pressure
        Pressure of pump over time.
        --------------------------------------------------------''' 
        tic0 = time.time()
        plotname = 'Pump Pressure Direct '
        plotname2 = 'AdjustedPressure'
        print('- Plotting ',bc,plotname)
        OTDateTime,PumpPres = rp.TruncateList(OTs,PumpPressure1) 
        pAbsPos = np.array(PumpPres)
        NewDT=pd.to_datetime(OTDateTime)
        Mintime = min(NewDT)
        DeltaSecs = []
        for jj, item in enumerate(NewDT):
            delta = (NewDT[jj]-Mintime).total_seconds()
            DeltaSecs.append(delta)
        ymin = -1000.0
        ymax = np.max(pAbsPos)*1.1
        yrange=[ymin,ymax]
        horlabel='Time'
        fig10 = rp.stats_2D_plot(DeltaSecs,pAbsPos,bc,CCTname,plotname,'Pump PSI',yrange,horlabel)
        toc0 = (time.time() - tic0)
        print(formattime.format(toc0))
        print()              
        PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+' '+plotname+' '+CCTname+'.png'
        try:
            plt.savefig(PDFPathPlusName,bbox='tight')
        except RuntimeError:
            print('No Plot -SaveFig error')
        plt.close('all')

        '''----------------------------------------------------
        Plot[15] Pump Relativeand Force Pressure right after first pressurization move
        Pressure of pump over time.
        --------------------------------------------------------''' 
        tic0 = time.time()
        plotname = 'Pump Pressure Dual'
        print('- Plotting ',bc,plotname)
        NewDT=[]
        pres2plot1=[]
        pres2plot2=[]
        findmove='5000' # looking for a 5000 move and corresponding pressures
        Prun = PumpMoveRequest
        for kk, mv in enumerate(Prun):
            newlist3=re.split(' ',str(mv))
            newlist1=re.split(' ',str(PumpPressure1[kk]))
            newlist2=re.split(' ',str(AdjustedPressure[kk]))
            for ib, nl in enumerate(newlist3):
                if nl == findmove:
                    if len(newlist1)>ib:
                        temp1=np.float(newlist1[ib])
                    else:
                        temp1=0
                    if len(newlist2)>ib:
                        temp2=np.float(newlist2[ib])
                    else:
                        temp2=0
                    if np.isnan(temp1):
                        temp1=0
                    if np.isnan(temp2):
                        temp2=0
                    pres2plot1.append(temp1)
                    pres2plot2.append(temp2)
                    NewDT.append(OTs[kk])
        try:
            Mintime = min(NewDT)
            DeltaSecs = []
            for jj, item in enumerate(NewDT):
                delta = (NewDT[jj]-Mintime).total_seconds()
                DeltaSecs.append(delta)
            ymin = -1000.0
            ymax = np.max(pres2plot2)*1.1
            yrange=[ymin,ymax]
            horlabel='Time'
            fig10 = rp.Dual_2D_plot(DeltaSecs,pres2plot1,pres2plot2,bc,CCTname,plotname,plotname2,'Pump PSI (adjusted)',yrange,horlabel)
            toc0 = (time.time() - tic0)
            print(formattime.format(toc0))
            print()              
            PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+' '+plotname+' '+CCTname+'.png'
            try:
                plt.savefig(PDFPathPlusName,bbox='tight')
            except RuntimeError:
                print('No Plot -SaveFig error')
            plt.close('all')
        except:
            print([str(bc)+plotname+' -Exception error - probably malformed time data'])

        '''----------------------------------------------------
        Plot[16] 3D Data Collection Times data 
        Stats, histogram + time plot
        --------------------------------------------------------''' 
        tic0 = time.time()
        plotname = '3D data collection times'
        print(' Plotting ',bc,plotname)
        Total=[]
        SearchAttemptCount=0
        TrackAttemptCount=0 #Keep track of attempt counts
        D3CalAttemptCount=0
        PPsAttemptCount=0
        StackAttemptCount=0
        StackCount=0
        DataCount=0
        Search=[]
        Tracktime=[]
        D3Caltime=[]
        PPtime=[]
        Stacktime=[]  
        Tottime=[]
        if len(OTs)>1000:  #don't bother plotting <500 data points
            for ii,val1 in enumerate(Track_dt):
                Icnts,Itime0 = AddUpAttempts(Search_dt[ii])
                SearchAttemptCount +=Icnts
                Search.append(Itime0)
                Icnt,Itime1 = AddUpAttempts(val1)
                TrackAttemptCount +=Icnt
                Tracktime.append(Itime1)
                Icnt,Itime2 = AddUpAttempts(D3Cal_dt[ii])
                D3CalAttemptCount +=Icnt
                D3Caltime.append(Itime2)
                Icnt,Itime3 = AddUpAttempts(PP_dt[ii])
                PPsAttemptCount +=Icnt
                PPtime.append(Itime3)
                Icnt,Itime4 = AddUpAttempts(Stack_dt[ii])
                StackAttemptCount +=Icnt
                Stacktime.append(Itime4)
                temptot = Itime1+Itime2+Itime3+Itime4
                Tottime.append(temptot)
                Tmin = np.min(Tottime)
                Tmax = np.max(Tottime)
                tempS3D = temptot+Itime0
                Total.append(tempS3D)
                DataCount=ii
            
            efficiency = StackAttemptCount/DataCount
            print(str(bc)+' DataCollection Efficiency: '+str(efficiency))  
            print
            yrange = [Tmin-.10,Tmax+.1] 
            pn = 'Tracking'
            fig2 = rp.stats_hist_time_plot(OTs,Tracktime,bc,CCTname,pn,'seconds',2)
            PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+'_'+pn+'_'+CCTname+'.png'
            print()              
            try:
                plt.savefig(PDFPathPlusName,bbox='tight')
            except RuntimeError:
                print('No Plot -SaveFig error')    
            pn = 'D3Cal'
            fig3 = rp.stats_hist_time_plot(OTs,D3Caltime,bc,CCTname,pn,'seconds',3)
            PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+'_'+pn+'_'+CCTname+'.png'
            print()              
            try:
                plt.savefig(PDFPathPlusName,bbox='tight')
            except RuntimeError:
                print('No Plot -SaveFig error')  
            pn ='PPtime'
            fig4 = rp.stats_hist_time_plot(OTs,PPtime,bc,CCTname,pn,'seconds',3)
            PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+'_'+pn+'_'+CCTname+'.png'
            print()              
            try:
                plt.savefig(PDFPathPlusName,bbox='tight')
            except RuntimeError:
                print('No Plot -SaveFig error')  
            pn = 'Stacktime'
            fig5 = rp.stats_hist_time_plot(OTs,Stacktime,bc,CCTname,pn,'seconds',2)
            PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+'_'+pn+'_'+CCTname+'.png'
            print()              
            try:
                plt.savefig(PDFPathPlusName,bbox='tight')
            except RuntimeError:
                print('No Plot -SaveFig error')  
            pn = 'Total_3D_time'
            fig6 = rp.stats_hist_time_plot(OTs,Tottime,bc,CCTname,pn,'seconds',2)
            PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+'_'+pn+'_'+CCTname+'.png'        
            toc0 = (time.time() - tic0)
            print(toc0)
            print()              
            try:
                plt.savefig(PDFPathPlusName,bbox='tight')
            except RuntimeError:
                print('No Plot -SaveFig error')
            pn = 'Search_time'
            fig6 = rp.stats_hist_time_plot(OTs,Search,bc,CCTname,pn,'seconds',2)
            PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+'_'+pn+'_'+CCTname+'.png'        
            toc0 = (time.time() - tic0)
            print(toc0)
            print()              
            try:
                plt.savefig(PDFPathPlusName,bbox='tight')
            except RuntimeError:
                print('No Plot -SaveFig error') 
            pn = 'SearchAnd3D_time'
            fig6 = rp.stats_hist_time_plot(OTs,Total,bc,CCTname,pn,'seconds',2)
            PDFPathPlusName = plotspathSummary+'\\'+BarcodeStartTime+'BC_'+str(bc)+'_'+pn+'_'+CCTname+'.png'        
            toc0 = (time.time() - tic0)
            print(toc0)
            print()              
            try:
                plt.savefig(PDFPathPlusName,bbox='tight')
            except RuntimeError:
                print('No Plot -SaveFig error')  


print('done')



