"""
Log2CSV Creator

This is modified from the Daily Times Histogram script. It searches
a designated directory and it's sub directories.

This data parser uses the Panda's data frame to store data from a runlog into
into a CSV data frame format. It can be run multiple times to add new data.

CSV should be usable in Excel for plotting data.

Data can be read into Python scripts (Pandas dataframe) for plotting as well.

jwh 9/18/14.
updated Rev2 2/5/15 - much faster operation with mmap search
updated Rev8 6/20/15 - handles new prefixes in runlogs
updated Rev9 9/8/15 - added ambient, case, illuminator temperature collumns and moved position of restart and timeout
updated RevC 11/18/16 - add new categories for timing STATEs recording
updated RevC 12/19/16 - fixed bug that overran excel cells with data larger than 32K and added overhead to STATES
Did not change rev because SW-Delay collumn will be added with new data that contains it.
"""
FunctName = 'Log2CSV_revC Creator'
LastFileName =''
SavedFileName = 'LogData_RC'  #output CSV file name - increase Rev after significant change

import os
import mmap
import pandas as pd
from collections import OrderedDict
import sys
import re
import datetime as dt
#import statistics as stats
import numpy as np
#import matplotlib.pyplot as plt
import matplotlib.dates
matplotlib.use('Qt5Agg')

# test for float value from string
def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# Below def(s) are file search processes turned into functions for later use
#----------------------------------------------------------------------------------
def SnS(inputlist):
    ''' String -n- Strip a list - This turns a list into a space delimitted string
    and strips the bracket characters from each end if they exist.  Use includes creating an Excel or CSV
    friendly entry into a DataFrame.'''
    newStr=''
    ttmp=''
    for ii,LL in enumerate(inputlist):
        ttmp = str(LL)
        if LL=='[' or LL==']' or LL==',' or LL==' ' or LL=='\t' or LL=='\n':
            ttmp =''
    newStr = newStr+ttmp+' '
    return newStr
# Below def(s) are file search processes turned into functions for later use
#----------------------------------------------------------------------------------
def U32K(String1):
    ''' Function test length of string to be less than 32K characters 
    (for excel limits).  If greater than, data is truncated at first space character
    less than 32K.  If less than or equal to 32K -it returns string unchanged
    '''
    sz = len(String1)
    LenLimit = 32000
    if sz > LenLimit:
        newlen = String1[0:LenLimit].rfind(' ')
        newStr = String1[0:newlen]
    else:
        newStr = String1
    return newStr

#----------------------------------------------------------------------------------
def GetFirstLineWith(term,offset):
    ''' Find first of occurrances of term between offset and end of fmm
    in global fmm variable (mmap). Return the line as text. Return first
    position after line.
    '''
    end = '\n'
    endline = end.encode('UTF-8')
    searchbytes = term.encode('UTF-8')
    position0 = -1
    position1 = fmm[offset:].find(searchbytes)
    if position1 >-1:
        positiona = fmm.rfind(endline,0,offset+position1)+1
        fmm.seek(positiona)
        firstline = fmm.readline()
        firstline = firstline.decode("utf-8")
        position0 = positiona+len(firstline)
        fmm.seek(position0)
    else:
        firstline = ''
    return firstline, position0
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
def GetLinesWith(term):
    ''' Return a list of all the lines with term in them'''
    Linist = []; txt = 'a';loc1 = 0; test =1
    while test:
        test = (not(txt=='') and not(loc1==-1))
        txt,loc1 = GetFirstLineWith(term,loc1)
        if not(txt==''):
            Linist.append(txt)
    return Linist
#----------------------------------------------------------------------------------

#CONSTANTS
micron2mm = 1000
PSI_Offset = 0
PSI2Atmosphere = 14.6959488

FunctInfo= ''
'''
An ordered dictionary called 'valueKeys' is constructed as
{'collumn name': ['unique data search string',valuecode]}

valueKey dict structure defines all the dataframe collumns, and the text
to search for as well as actions after that text is found (using the value code).

Log2CSV_rev2 searches data matching a search string and records a single value
that follows it.

The first file value in the runlog is captured per dictionary item and
produces a comma delimited data frame row for each runlog file.

Value codes of 0 will search for pattern in log and collects the first value
after search term.

Value codes greater than 0 are special instructions for data collection such as
collect the string delimited in a special way or collect rest of string in line.

Filename values makeup the first four dictionary items and are not searched for.

If the search term is '' , the search is skipped.  However the column may be filled
in a substring search of the line or another way based on the find code.

Findcode in dictionary tuple directs an if/else action on the dictionary searches.
In most cases the findcode branches to find multiple substrings in the line or subsequent
to the line.  In some cases, calculations are performed based on the findcode.
The Findcode branches code to the correct code.
'''

valueKeys = OrderedDict()
valueKeys['File_Name']=['',0]
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

valueKeys['Stop_DeltaT']=[':Time to stop ,',0] # from setup tracking to longitudinal motor stop
valueKeys['Obj_Found_TS']=[':Setup Tracking',6]
valueKeys['StopFlow_TS']=[':Time to stop ,',6]
valueKeys['ObjXMin']=[':Min AbsX During Rotation,',0]
valueKeys['ObjXMax']=[':Max AbsX During Rotation,',0]
valueKeys['Cap_Z_Center']=[':Focus Centroid,',0] # units = microns
valueKeys['Cap_Y_Center']= [':Y Centroid,',0] # units = microns
valueKeys['Angle']=[':Angle,',0] # degrees
valueKeys['FlowRadius_rough']=[':Radius,',0] # microns
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
valueKeys['FlowRadius_refined']=['capradius=',8] #millimeters
valueKeys['Rot_Offset']=['rotationoffset=',0] # degrees

valueKeys['C3D_Status']=[':c3d status=',10]
valueKeys['C3D_TS']=['',10] # microns
valueKeys['C3D_Count']=['',10] # microns
valueKeys['C3D_CapCenter_Y']=['',10] # microns
valueKeys['C3D_CapCenter_Z']=['',10] # microns
valueKeys['C3D_CapRadius']=['',10] # microns
valueKeys['C3D_RotationOffset']=['',10]
valueKeys['C3D_MidAbsX']=['',10]
valueKeys['C3D_MidRelX']=['',10]
valueKeys['C3D_PPCount']=['',10]
valueKeys['C3D_Msg']=['',10]
valueKeys['TarObj_ID']=[':tar ',9] # no units
valueKeys['Tar_TS']=['',9] 
valueKeys['Tar_Count']=['',9]
valueKeys['Tar_FID0']=['',9] # no units
valueKeys['Tar_FID']=['',9] # no units
valueKeys['Tar_PI']=['',9] # no units
valueKeys['Tar_RelLon']=['',9] # no units
valueKeys['Tar_RelLat']=['',9] # no units
valueKeys['Tar_AbsLon']=['',9] # no units
valueKeys['Tar_AbsLat']=['',9] # no units
valueKeys['Tar_AbsFoc']=['',9] # no units
valueKeys['Tar_AbsVel']=['',9] # no units
valueKeys['Tar_Area']=['',9] # no units
valueKeys['Tar_Dens']=['',9] # no units
valueKeys['Tar_Mul']=['',9] # no units
valueKeys['Tar_Class']=['',9] # no units
valueKeys['HPIObj_ID_Sel']=[':hpic3d send3dldt=true',9] # no units
valueKeys['HPI_TS']=['',9]
valueKeys['HPI_Count']=['',9]
valueKeys['HPI_CapCtr_Y']=['',9]
valueKeys['HPI_CapCtr_Z']=['',9]
valueKeys['HPI_Repeat']=['',9]
valueKeys['Imo_TS']= [':imo ',13]
valueKeys['ImoObj_ID']=['',13] # no units
valueKeys['Imo_count']=['',13]
valueKeys['Imo_FID0']=['',13] # no units
valueKeys['Imo_FID']=['',13] # no units
valueKeys['Imo_Indx']=['',13] # no units
valueKeys['Imo_PI']=['',13] # no units
valueKeys['Imo_RelLon']=['',13] # no units
valueKeys['Imo_RelLat']=['',13] # no units
valueKeys['Imo_AbsLon']=['',13] # no units
valueKeys['Imo_AbsLat']=['',13] # no units
valueKeys['Imo_AbsFoc']=['',13] # no units
valueKeys['Imo_AbsVel']=['',13] # no units
valueKeys['Imo_TDelta']=['',13] # no units
valueKeys['Imo_Area']=['',13] # no units
valueKeys['Imo_Dens']=['',13] # no units
valueKeys['Imo_Class']=['',13] # no units
valueKeys['StopDeltaT']=['',13]
valueKeys['StopVel']=['',13]
valueKeys['Pump_StartTime']=[':Start Pump',6] # time pump commanded to pressureize
valueKeys['Idle_dt']=['STATE DELTA TIME,Idle',15] # Recorded Stack Time (previous data set)
valueKeys['SW_Delay_dt']=['STATE DELTA TIME,Overhead',15]
valueKeys['Stack_dt']=['STATE DELTA TIME,Stack',15] # Recorded Stack Time (previous data set)
valueKeys['Search_dt']=['STATE DELTA TIME,Search',15] # Record all the Search times in log comma delimited
valueKeys['Search_dt_cnt'] = ['',15]
valueKeys['Track_dt']=['STATE DELTA TIME,Track',15] # Tracking/stopping time find all the lines with this key word and comma delimit in a
valueKeys['Track_dt_cnt'] = ['',15]                   # in a single text entry into a cell.
valueKeys['D3Cal_dt']=['STATE DELTA TIME,3D Cal',15]
valueKeys['D3Cal_dt_cnt'] = ['',15]
valueKeys['PP_dt']=['STATE DELTA TIME,PP',15]
valueKeys['PumpMoveRequest']=['rtmmot pum mov',16] 
valueKeys['PumpMoveRequestTS']=['',16]
valueKeys['PumpMoveResponse']=['rtmnotify pum',17]
valueKeys['PumpMoveResponseTS']=['',17]
valueKeys['PumpStrPot']=['rtmmea pummm',18] # must find the first rtmmea after line with 'rtmmea pummm'
valueKeys['PumpStrPotTS']=['',18]
valueKeys['PumpPressure1']=[' psi',19] # time stamp and psi reading as tuple
valueKeys['PumpPressure1TS']=['',19] 
valueKeys['AdjustedPressure']=['Adjusted Pressure,',20] # time stamp and psi reading as tuple
valueKeys['AdjustedPressureTS']=['',20]
valueKeys['ERROR']= [':ERROR:',21]
valueKeys['ERROR_Count']= ['',21]
Fnames =[] # Initialize the list for filenames
# defines some common Data-time formats in the Datetime module definitions
TimeFormat = "%Y%m%d%H%M%S"
TimeFormatb = "%Y-%m-%d %H:%M:%S"
FMTuS = "%H:%M:%S.%f"

#constants for system
FramesPerSecond = 998.002
CapDia = .062
PI = 4.0*np.arctan(1)
MFRAD2 =0 # flag and value for improved radius info.
specimenCat = 'uninitialized'

# Variables initialized
ObjectID=-1

#Delimeters used
delimf = '='+'|'+',' +'|'+ '  '+'|'+chr(13)+'|'+chr(11)+\
         '|'+chr(10)+'|'+chr(32)+'|'+chr(9)
delimc = ':'+'|'+',' +'|'+ '  '+'|'+chr(13)+'|'+chr(11)+\
         '|'+chr(10)+'|'+chr(32)+'|'+chr(9)
# '\.'+ '\.'+chr(58) +'|'+'_'+'|' not used delimeter characters
delimr = ' '+'|'+',' +'|'+'  '

label_term=list(valueKeys.keys())
lt_cnt = len(label_term)

print('')
print('--------------------------')
print('Search log files for these ',lt_cnt,' labels: ',label_term)

print('');print('--------------------------');print('');
print(FunctInfo);print(' ')
print(FunctName); print(' '); print(' '); print(' ')
pth1 = input('Enter path to directory of log directories:  ')
t0 = dt.datetime.now()
#'\\\\lancer\\upload\\abbott\\cct034\\gservlog\\ucm\\cct034_201409';#
#LogFiles = os.listdir(pth1)
Dir_names = []
Dir_names_candidate = [f for f in os.listdir(pth1) if os.path.isdir(os.path.join(pth1,f))]
Dir_names_candidate = sorted(Dir_names_candidate)
StopFlow_hold = '' # flag for holding data until next row (or next log file).
flowVelocity_hold=''

for dc,dn in enumerate(Dir_names_candidate): #Logs are stored in daily directories - so look for numbered directories
    try:
        dx=float(dn)
        # we only want directories labeled as numbers for days of the month so it must be a number
        # if someone decides to name a directory '100' then it would take that as a number
        # names that float() cannot convert to a number are rejected.
    except ValueError:
        print('Not a day of month - skipping directory ',dn)
        continue
    Dir_names.append(Dir_names_candidate[dc])
Dir_names_sorted= sorted(Dir_names)
Dir_count = len(Dir_names_sorted)

#Dir_names = Dir_names[0:Dir_count]

print('Found: '+str(Dir_count)+' Directories')
print('Directories are: ',Dir_names_sorted);print();
for n in range(40):print('-',end='')
print()

#With the addition of pump and object flow data, files are now too large for Python Pandas module. (100MByte+)
#So the strategy is break files up into Barcode entities that are less than <100Mbyte at which point 
#the barcode will be split into files of less than 100MB.
PathPlusName = pth1+'\\'+SavedFileName+'.csv'  #path and name of data file
Testfile =''
if os.path.isfile(PathPlusName):  # if file exists append if not start new
    Data3 = pd.read_csv(PathPlusName, low_memory=False) # read all the data back into the variables forprocessing
    Data3.sort(columns=['File_Name'])
    LastRow = len(Data3)-1
    TestRow = len(Data3)-1
    Testfile = str(Data3.ix[LastRow,'File_Name'])
    DirStart = str(int(float(str(Data3.ix[LastRow,'File_Dir']))))
    print('Last entry in CSV: ', PathPlusName)
    print('Last Row: ',LastRow)
    print('Last Dir: ',DirStart)
    print('Last File Name: ',Testfile)
    LastFileName = Testfile
    print()
else:
    # create a row data initializer of the right size
    #outfile = open(PathPlusName, 'wb')
    Data3 = pd.DataFrame(columns=label_term)
    # Initializes table with collumn headers
    #Data3.to_csv(pth1+'\\'+SavedFileName+'.csv',index=False)
    #outfile.close()
    LastFileName = ''
    DirStart = Dir_names_sorted[0]
    LastRow =0
for n in range(40):print('-',end='')
print()
#---------------------------------------------------------------------------
# THE MAIN DATAFRAME INDEX is 'row' variable
    #initialized to zero if no CSV file exist and one if it doesn't
row = LastRow+1 # start the row counter at last row number + 1 in case of first index it will be 1
dc_count =1 # initialize data collection counter for per stop data collection counting.
SampType ='Uninitialized' #initialize persistant value SampType - shows up in one file and
# applys to all subsequent files until another shows up.
PumpStartFlag = 0
fstopflagold = 0
fstopnew = 0
dcflag = 0
dctime = 0

DirRange =Dir_names_sorted[Dir_names_sorted.index(DirStart):]
# If not starting with first directory, set the range of search
FstopTS = 0
SearchTime =-1
fstopflagold = 0
DCdeltaTSeconds = -1
for tempdir in DirRange:
    temp_path = pth1+"\\"+tempdir
    print('Working in directory: ', temp_path)
    Fnames=[] #clear the list to use in the next directory
    file_list = os.listdir(temp_path)
    file_list.sort()
    for file in file_list:
        if file.endswith(".log"):
            Fnames.append(file)
    if tempdir == DirStart:
        if not(LastFileName == ''):
            LastFileName = Fnames[-1]
        if LastFileName =='':
            FnamesStartIndex = 0
        else:
            FnamesStartIndex = Fnames.index(LastFileName) +1
    else:
        FnamesStartIndex = 0
    Fnsize = len(Fnames[FnamesStartIndex:])

    skipcount=0
    for jj,stepFile in enumerate(Fnames[FnamesStartIndex:]):
        filesleft = Fnsize-jj
        print(stepFile+'   '+str(filesleft)+'            ', end='\r')
    # for each log file in directory assign file name info
        full_path_and_name = temp_path+'\\'+stepFile
        filesize = os.path.getsize(full_path_and_name)
        if filesize>10000000:  #skip big files
            print('skipping '+full_path_and_name+' file >10M '+str(filesize))
            skipcount=skipcount+1
            continue
        fi = open(full_path_and_name,'r')
        temp = re.split('_',stepFile.split('.')[0])
        tmptime=temp[1]+temp[2]
        machine = temp[0]
        tstlist = list(tmptime)
        if tstlist[-2]=='6': # occasionally log files record seconds as 60
        #back up a second if the 60 second record error has occurred  
        # it's a small infrequent error in time stamps, but timedate functions cannot handle it
            tstlist[-2]='5'
            tstlist[-1]='9'
        tmptime="".join(tstlist)
        try:
            intermedTime =dt.datetime.strptime(tmptime,TimeFormat)
# we only want directories labeled as numbers for days of the month
        except ValueError:
            print('Bad date time ',tmptime, '  skipping')
            continue
        Data3 = Data3.reset_index(drop=True)
        Data3.loc[row,'File_Name']=stepFile
        Data3.loc[row,'File_Dir']= tempdir
        Data3.loc[row,'CCT_Name']=machine
        Data3.loc[row,'File_Time']=intermedTime
        Data3.loc[row,'Bar_Code']=-1 # Initialize Barcode to an integer incase it is missing.

#now search lines in log file
        try:
            fmm = mmap.mmap(fi.fileno(),0, access=mmap.ACCESS_READ)
        except ValueError:
            print(tempdir,' ', stepFile,'File couldn\'t be read (empty?) ')

        for kk in label_term[4:]:
#find search terms from Bar_Code on in log file
            txt2find,findcode = valueKeys[kk]
            line2decode,loc1 = GetFirstLineWith(txt2find,0)
            #print(row, txt2find, line2decode)
            if loc1 > -1 and not(txt2find==''): # found a match if >-1
                #-----------------------------------------------------------------------------
                if findcode == 0: # return first term after search term
                    ptr = line2decode.index(txt2find)+len(txt2find)
                    wordlist = re.split(delimf,line2decode[ptr:])
                    #grab value right after search term
                    grabValue = wordlist[0]
                    Data3.loc[row,kk]=U32K(grabValue)
                #-----------------------------------------------------------------------------
                elif findcode ==1: #find last occurrance in file of search value
                    tempList=GetLinesWith(txt2find)
                    lastInList = tempList[-1]
                    ptr = lastInList.index(txt2find)+len(txt2find)
                    wordlist = re.split(delimf,lastInList[ptr:])
                    grabValue = wordlist[0]
                    specimenCat = U32K(grabValue) # persistent variable only shows up in logs where
                    # specimen changes - recoreded for every log entry after it occurs/changes
                #-----------------------------------------------------------------------------
                elif findcode==2:
                    #Label this row with timeout detection
                    Data3.loc[row,kk]='Timeout'

                #-----------------------------------------------------------------------------
                elif findcode==3:
                    # Capture everything in line after keyword
                    p1 = line2decode.find(txt2find)+len(txt2find)
                    grabValue = line2decode[p1:]
                    if txt2find=='focusvolt=':
                        Data3.loc[row,kk]=U32K(SnS(grabValue))
                    else:
                        Data3.loc[row,kk]=U32K(grabValue)
                #-----------------------------------------------------------------------------
                elif findcode==4:
                    #Label this row with UCM Restart
                    Data3.loc[row,kk]='UCM Restart'

                #-----------------------------------------------------------------------------
                elif findcode==5:
                    #Parse Wafer Classification Details as sub search for terms in 3dd line
                    tempList=GetLinesWith(txt2find)
                    for tl, tline in enumerate(tempList):
                        wordlist = re.split(delimf, tline)
                        IDtoFind = wordlist[(wordlist.index('id')+1)]
                        dexlist = Data3[Data3['File_Name'] == (IDtoFind+'.log')].index.tolist()
                        try:
                            dex = dexlist[0]
                        except IndexError:
                            #print(kk,'but no data index ->',txt2find,IDtoFind,findcode)
                            #print('templist is ',tempList)
                            #print('wordlist is ',wordlist)
                            #print('ID to find is ', IDtoFind)
                            #print('dexlist is ', dexlist)
                            dex = row
                        Data3.loc[dex,'WaferID'] = IDtoFind
                        Data3.loc[dex,'WaferStatus']= wordlist[(wordlist.index('status')+1)]
                        try: # depending on status this may not be present
                            Data3.loc[dex,'WaferClass'] = wordlist[(wordlist.index('class')+1)]
                        except ValueError:
                            Data3.loc[dex,'WaferClass'] =''
                #-----------------------------------------------------------------------------
                elif findcode==6: #Findcode records timestamp from lines where keywords occur
                    wordlist = re.split(delimf,line2decode)
                    Data3.loc[row,kk] = wordlist[2]
                #-----------------------------------------------------------------------------
                elif findcode==7:  # This findcode parses and calculates mass flow parameters
                    ptr = line2decode.index(txt2find)+len(txt2find)
                    wordlist = re.split(delimf,line2decode[ptr:])
                    try:
                        AtmPress = (float(wordlist[0]))/PSI2Atmosphere 
                    except ValueError:
                        print(stepFile,wordlist[0], ' unexpected value')
                    if AtmPress<0:
                        AtmPress =0
                    try:
                        MFRad = float(wordlist[2])/micron2mm #work in mm
                    except ValueError:
                        print(stepFile, wordlist[2], ' unexpected value')
                    if MFRAD2 >0:
                        Rad2use = MFRAD2
                    else:
                        Rad2use = MFRad
                    # use the rotational radius estimate for mass flow if it exists...
                    try:
                        ObjVel = float(wordlist[4])/micron2mm #work in mm
                    except ValueError:
                        print(stepFile, wordlist[4], ' unexpected value')
                    if ObjVel<0:
                        ObjVel =-1
                        PkVelEst = -1
                    else:
                        RadRatioSq = (Rad2use/(CapDia/2))**2
                        PkVelEst = ObjVel/(1-RadRatioSq)
                    MFAvg = PkVelEst/2
                    if PkVelEst > 1e-6 and AtmPress > 0:
                        FlowR = AtmPress/MFAvg  #atmospheres/mm^3/second
                    else:
                        FlowR = -1
                    MFlow = MFAvg*PI*(CapDia/2)**2

                    Data3.loc[row,'BarPressMF'] = AtmPress
                    Data3.loc[row,'RadMF']      = MFRad
                    Data3.loc[row,'ObjVel']     = ObjVel
                    Data3.loc[row,'MFVel']      = MFAvg
                    Data3.loc[row,'PkVel']      = PkVelEst
                    Data3.loc[row,'MassFlow']   =MFlow
                    Data3.loc[row,'FlowResistance'] = FlowR
                    MFRAD2=0
                #-----------------------------------------------------------------------------
                elif findcode==8:
                    ptr = line2decode.index(txt2find)+len(txt2find)
                    wordlist = re.split(delimf,line2decode[ptr:])
                    MFRAD2 = float(wordlist[0])/1000 # convert to mm
                    Data3.loc[row,kk]=MFRAD2
                #-----------------------------------------------------------------------------
                elif findcode==9: #targets and selected object tracking data                    
                    tempList=GetLinesWith(txt2find)                    
                    if txt2find==':tar ':
                        Tar_objid='';Tar_fid0 ='';Tar_fid ='';Tar_pi ='';Tar_rellon ='';Tar_rellat =''
                        Tar_relvel ='';Tar_abslon ='';Tar_abslat ='';Tar_absfoc ='';Tar_absvel ='';
                        Tar_rot=''; Tar_area=''; Tar_dens=''; Tar_class=''; jj=0; Tar_ts='';Tar_mul='';ck=0
                        for jj, line2decode in enumerate(tempList): #collect all tar values for each variable
                        # into a string then save the strings under propper heading.
                            line2decode = line2decode.replace('(','').replace(')','') # eliminate the parens
                            wordlist = re.split(delimf, line2decode)
                            Tar_objid  += wordlist[(wordlist.index('objid')+1)]+' '
                            Tar_ts     += wordlist[2]+' '
                            Tar_fid0   += wordlist[(wordlist.index('fid0')+1)]+' '
                            Tar_fid    += wordlist[(wordlist.index('fid0')+3)] +' '  #aliasing problem with fid and fid0 so just use offset from fid0 which is unique
                            Tar_pi     += wordlist[(wordlist.index('pi')+1)]  +' '
                            Tar_rellon += wordlist[(wordlist.index('rel')+1)] +' '
                            Tar_rellat += wordlist[(wordlist.index('rel')+2)] +' '
                            Tar_relvel += wordlist[(wordlist.index('relv')+1)]+' '
                            Tar_abslon += wordlist[(wordlist.index('abs')+1)] +' '
                            Tar_abslat += wordlist[(wordlist.index('abs')+2)] +' '
                            Tar_absfoc += wordlist[(wordlist.index('abs')+3)] +' '
                            Tar_absvel += wordlist[(wordlist.index('absv')+1)]+' '
                            Tar_rot    += wordlist[(wordlist.index('rot')+1)] +' '
                            Tar_area   += wordlist[(wordlist.index('area')+1)]+' '
                            try:
                                Tar_dens   += wordlist[(wordlist.index('dens')+1)]+' '
                            except ValueError:
                                ck +=1
                            try: 
                                Tar_mul += wordlist[(wordlist.index('mul')+1)]+' '
                            except ValueError:
                                ck +=1
                            Tar_class  += wordlist[(wordlist.index('class')+1)]+' '
                        Data3.loc[row,'TarObj_ID']  =U32K(Tar_objid[0:-1]) #eliminate trailing space character
                        Data3.loc[row,'Tar_TS']     =U32K(Tar_ts[0:-1])
                        Data3.loc[row,'Tar_FID0']   =U32K(Tar_fid0[0:-1])
                        Data3.loc[row,'Tar_FID']    =U32K(Tar_fid[0:-1])
                        Data3.loc[row,'Tar_PI']     =U32K(Tar_pi [0:-1])
                        Data3.loc[row,'Tar_RelLon'] =U32K(Tar_rellon[0:-1])
                        Data3.loc[row,'Tar_RelLat'] =U32K(Tar_rellat[0:-1])
                        Data3.loc[row,'Tar_RelVel'] =U32K(Tar_relvel[0:-1])
                        Data3.loc[row,'Tar_AbsLon'] =U32K(Tar_relvel[0:-1])
                        Data3.loc[row,'Tar_AbsLat'] =U32K(Tar_abslat[0:-1])
                        Data3.loc[row,'Tar_AbsFoc'] =U32K(Tar_absfoc[0:-1])
                        Data3.loc[row,'Tar_AbsVel'] =U32K(Tar_absvel[0:-1])
                        Data3.loc[row,'Tar_AbsRot'] =U32K(Tar_rot[0:-1])
                        Data3.loc[row,'Tar_Area']   =U32K(Tar_area[0:-1])
                        Data3.loc[row,'Tar_Dens']   =U32K(Tar_dens)  #sometimes not present
                        Data3.loc[row,'Tar_Mul']    =U32K(Tar_mul)
                        Data3.loc[row,'Tar_Class']  =U32K(Tar_class[0:-1])
                        Data3.loc[row,'Tar_Count']  =str(len(tempList))
                    elif txt2find==':hpic3d send3dldt=true':
                        Hpi_id =''; Hpi_ts=''; Hpi_capcentery='';Hpi_capcenterz='';Hpi_repeat=''
                        for jj, line2decode in enumerate(tempList):
                            wordlist = re.split(delimf, line2decode) # no parens to worry about
                            Hpi_id           += wordlist[(wordlist.index('objectid')+1)]+' '
                            Hpi_ts           += wordlist[2]+' '
                            Hpi_capcentery   += wordlist[(wordlist.index('capcentery')+1)]+' '
                            Hpi_capcenterz   += wordlist[(wordlist.index('capcenterz')+1)]+' '
                            Hpi_repeat       += wordlist[(wordlist.index('repeat')+1)]+' '
                        Data3.loc[row,'HPIObj_ID_Sel']=U32K(Hpi_id[0:-1]) #eliminate trailing space character
                        Data3.loc[row,'HPI_TS']       =U32K(Hpi_ts[0:-1])
                        Data3.loc[row,'HPI_Count']    =U32K(str(len(tempList)))
                        Data3.loc[row,'HPI_CapCtr_Y'] =U32K(Hpi_capcentery[0:-1])
                        Data3.loc[row,'HPI_CapCtr_Z'] =U32K(Hpi_capcenterz[0:-1])
                        Data3.loc[row,'HPI_Repeat']   =U32K(Hpi_repeat[0:-1])
         #-----------------------------------------------------------------------------
                elif findcode == 10: #Parse Wafer Classification Details &subsearch c3d lines and search for subsequent tar with capture ObjectID to record area, index, & velocities
                    tempList=GetLinesWith(txt2find)
                    C3D_status=''; C3D_capcentery = '';C3D_capcenterz='';C3D_capradius=''; C3D_rotationoffset =''
                    C3D_midabsx =''; C3D_midrelx ='';C3D_ppcount ='';C3D_msg ='';C3D_ts=''; C3D_count=''
                    if kk== 'C3D_Status':
                        for jj, line2decode in enumerate(tempList):
                            wordlist = re.split(delimf, line2decode)
                            testtmp =wordlist[(wordlist.index('status')+1)]
                            C3D_status +=  testtmp+' '
                            C3D_ts += wordlist[2]+' '
                            C3D_capcentery += wordlist[(wordlist.index('capcentery')+1)]+' '
                            C3D_capcenterz += wordlist[(wordlist.index('capcenterz')+1)]+' '
                            C3D_capradius += wordlist[(wordlist.index('capradius')+1)] +' '
                            C3D_rotationoffset += wordlist[(wordlist.index('rotationoffset')+1)] +' '
                            C3D_midabsx += wordlist[(wordlist.index('midabsx')+1)] +' '
                            C3D_midrelx += wordlist[(wordlist.index('midrelx')+1)] +' '
                            C3D_ppcount += wordlist[(wordlist.index('ppcount')+1)] +' '
                            if testtmp=='fail':
                                quoteslist = re.split('"',line2decode) # look for message between quotes
                                C3D_msg += quoteslist[1].replace(' ','_') # make the spaces in the message into underbars
                    Data3.loc[row,'C3D_Status']         = U32K(C3D_status[0:-1])   # [0:-1] removes trailing space character  
                    Data3.loc[row,'C3D_CapCenter_Y']    = U32K(C3D_capcentery[0:-1])
                    Data3.loc[row,'C3D_CapCenter_Z']    = U32K(C3D_capcenterz[0:-1])
                    Data3.loc[row,'C3D_Radius']         = U32K(C3D_capradius[0:-1])
                    Data3.loc[row,'C3D_RotationOffset'] = U32K(C3D_rotationoffset[0:-1])
                    Data3.loc[row,'C3D_MidAbsX']        = U32K(C3D_midabsx[0:-1])
                    Data3.loc[row,'C3D_MidRelX']        = U32K(C3D_midrelx[0:-1])
                    Data3.loc[row,'C3D_PPCount']        = U32K(C3D_ppcount[0:-1])
                    Data3.loc[row,'C3D_Msg']            = U32K(C3D_msg[0:-1])
                    Data3.loc[row,'C3D_TS']             = U32K(C3D_ts[0:-1])
                    Data3.loc[row,'C3D_Count']          = str(len(tempList))
        #------------------------------------------------------------------------
                elif findcode == 11: # return first term after search term
                    ptr = line2decode.index(txt2find)+len(txt2find)
                    wordlist = re.split(delimf,line2decode[ptr:])
                    #grab value right after search term
                    try:
                        bc = int(wordlist[0])
                    except ValueError:
                        print('ValueError: ',ptr,bc)
                        bc = -1  # set the barcode as a -1 for anything not an integer
                    Data3.loc[row,kk]=bc
        #------------------------------------------------------------------------
                elif findcode == 12: # return first term after search term
                    testptr = line2decode.index(txt2find)+len(txt2find)
                    tempwordlist = re.split(delimf,line2decode[testptr:])
                    temperature = ''
                    for lcnt,label in enumerate(tempwordlist):
                        if label == "degc":
                            temperature = tempwordlist[lcnt+1]
                    try:
                        temperature = float(temperature)
                    except:
                        print('Value error: ', testptr,temperature)
                        temperature = -100.0
                        
                    Data3.loc[row,kk]=temperature
        #------------------------------------------------------------------------
                elif findcode == 13: #Parse imo to gather slow down velocities into list
                #Parse imo and absv and fid as sub search for terms in imo lines to obtain two lists
                # but only for the same objid.
                    tempList=GetLinesWith(txt2find)  # get all the lines with :imo
                    Imo_objid='';Imo_fid0 ='';Imo_fid ='';Imo_indx =''; Imo_pi ='';Imo_rellon ='';Imo_rellat =''
                    Imo_relvel ='';Imo_abslon ='';Imo_abslat ='';Imo_absfoc ='';Imo_absvel ='';
                    Imo_area=''; Imo_focus=''; Imo_tdelta=''; jj=0; Imo_ts=''
                    for jj, line2decode in enumerate(tempList): #collect all tar values for each variable
                    # into a string then save the strings under propper heading.
                        line2decode = line2decode.replace('(','').replace(')','') # eliminate the parens
                        wordlist = re.split(delimf, line2decode)
                        Imo_objid  += wordlist[(wordlist.index('objid')+1)]+' '
                        Imo_ts     += wordlist[2]+' '
                        Imo_fid0   += wordlist[(wordlist.index('fid0')+1)]+' '
                        Imo_fid    += wordlist[(wordlist.index('fid0')+3)] +' '  #aliasing problem with fid and fid0 so just use offset from fid0 which is unique
                        Imo_indx   += wordlist[(wordlist.index('indx')+1)]  +' '
                        Imo_pi     += wordlist[(wordlist.index('pi')+1)]  +' '
                        Imo_rellon += wordlist[(wordlist.index('rel')+1)] +' '
                        Imo_rellat += wordlist[(wordlist.index('rel')+2)] +' '
                        Imo_relvel += wordlist[(wordlist.index('relv')+1)]+' '
                        Imo_abslon += wordlist[(wordlist.index('abs')+1)] +' '
                        Imo_abslat += wordlist[(wordlist.index('abs')+2)] +' '
                        Imo_absfoc += wordlist[(wordlist.index('abs')+3)] +' '
                        Imo_absvel += wordlist[(wordlist.index('absv')+1)]+' '
                        Imo_tdelta += wordlist[(wordlist.index('tdelta')+1)]+' '
                        Imo_area   += wordlist[(wordlist.index('area')+1)]+' '
                        Imo_focus   += wordlist[(wordlist.index('focus')+1)]+' '
                    Data3.loc[row,'ImoObj_ID']  =U32K(Imo_objid[0:-1]) #eliminate trailing space character
                    Data3.loc[row,'Imo_TS']     =U32K(Imo_ts[0:-1])
                    Data3.loc[row,'Imo_FID0']   =U32K(Imo_fid0[0:-1])
                    Data3.loc[row,'Imo_FID']    =U32K(Imo_fid[0:-1])
                    Data3.loc[row,'Imo_Indx']   =U32K(Imo_indx[0:-1])
                    Data3.loc[row,'Imo_PI']     =U32K(Imo_pi [0:-1])
                    Data3.loc[row,'Imo_RelLon'] =U32K(Imo_rellon[0:-1])
                    Data3.loc[row,'Imo_RelLat'] =U32K(Imo_rellat[0:-1])
                    Data3.loc[row,'Imo_RelVel'] =U32K(Imo_relvel[0:-1])
                    Data3.loc[row,'Imo_AbsLon'] =U32K(Imo_relvel[0:-1])
                    Data3.loc[row,'Imo_AbsLat'] =U32K(Imo_abslat[0:-1])
                    Data3.loc[row,'Imo_AbsFoc'] =U32K(Imo_absfoc[0:-1])
                    Data3.loc[row,'Imo_AbsVel'] =U32K(Imo_absvel[0:-1])
                    Data3.loc[row,'Imo_TDelta'] =U32K(Imo_tdelta[0:-1])
                    Data3.loc[row,'Imo_Area']   =U32K(Imo_area[0:-1])
                    Data3.loc[row,'Imo_Focus']  =U32K(Imo_focus[0:-1])
                    Data3.loc[row,'Imo_Count']  =str(len(tempList))
        #------------------------------------------------------------------------
                elif findcode == 14: # ':CellSeen' time and endof log time for 3D data collection estimate.
                    wordlist = re.split(delimf,line2decode)
                    psTime = wordlist[2]  #record start time of pump
                    Data3.loc[row,kk]  =Imo_focus[0:-1]
        #------------------------------------------------------------------------
                elif findcode == 15: #DELTA TIME,Search or idle, or stack, or track, or pp
                #Collect multiple lines with data following search term, combine data in 
                # space delimitted field entry into spreadsheet cell.
                    if kk=='D3Cal_dt':
                        listptr =9
                    else:
                        listptr =8
                    tempList=GetLinesWith(txt2find)  # get all the lines with search term
                    terms=''
                    times=''
                    for tl, tline in enumerate(tempList): #Find these terms in these lines and value that follows
                        wordlist = re.split(delimf, tline)
                        times += wordlist[2]+' '
                        terms += wordlist[listptr]+' '
                    try:
                        Data3.loc[row,kk]           =U32K(terms[0:-1])
                        Data3.loc[row,(kk+'_cnt')]  =len(tempList)
                        Data3.loc[row,(kk+'TS')]    =U32K(times[0:-1])
                    except ValueError:
                        print('Problem with '+kk+' record')
        #------------------------------------------------------------------------
                elif findcode == 16:                
                # Collect multiple lines with pump move data following search term, combine them 
                # space delimitted into separate entry that will be parsed when plotted. 
                #Collect and store their corresponding timestamps for timing plots of critical operations.
                #determine if pump move is positive or negative(reverse - depressurize) and add sign
                    tempList=GetLinesWith(txt2find)  # get all the lines with search term
                    termlist=[]
                    term_accum =''
                    time_accum=''
                    for tl, tline in enumerate(tempList): #Find these terms in these lines and value that follows
                        wordlist = re.split(delimf, tline)
                        time_value = str(wordlist[2])
                        rf_sign = wordlist[7]
                        mov_value = wordlist[8]
                        if rf_sign =='f':
                            newval=mov_value
                        else:
                            newval='-'+mov_value # add negative sign to reverse moves
                        term_accum += newval+' '
                        time_accum += time_value+' '
                    term_accum=term_accum[0:-1] #remove trailing space
                    time_accum = time_accum[0:-1]
                    try:
                        Data3.loc[row,kk]           =U32K(term_accum)
                        Data3.loc[row,(kk+'_cnt')]  =len(tempList)
                        Data3.loc[row,(kk+'TS')]    =U32K(time_accum)
                    except ValueError:
                        print('Problem with '+kk+' record')     
        #------------------------------------------------------------------------
                elif findcode == 17: 
                # Collect multiple lines with pump notify(absolute coord) data following search term, combine them 
                # comma delimitted into one entry that will be parsed when plotted. 
                #Collect and store their corresponding timestamps for timing plots of critical operations.
                    tempList=GetLinesWith(txt2find)  # get all the lines with search term
                    term_accum =''
                    time_accum =''
                    for tl, tline in enumerate(tempList): #Find these terms in these lines and value that follows
                        wordlist = re.split(delimf, tline)
                        mov_value = str(wordlist[11]) # absolute value of pump motor position
                        time_value = str(wordlist[2])
                        term_accum += mov_value+' '
                        time_accum += time_value+' '
                    term_accum=term_accum[0:-1] #remove trailing space
                    time_accum = time_accum[0:-1]
                    try:
                        Data3.loc[row,kk]           =U32K(term_accum)
                        Data3.loc[row,(kk+'_cnt')]  =len(tempList)
                        Data3.loc[row,(kk+'TS')]    =U32K(time_accum)
                    except ValueError:
                        print('Problem with '+kk+' record')  
        #------------------------------------------------------------------------  
                elif findcode == 18: 
                # searc for line as marker and then first line after with second marker, for all occurances in the file
                    term_accum ='' 
                    time_accum =''
                    tempList=GetLinesWith(txt2find)
                    ticker=0
                    for pp, ee in enumerate(tempList):
                        dummy1, dummy2 = GetFirstLineWith(txt2find,ticker)
                        tline,ticker = GetFirstLineWith('rtmmea',dummy2)
                        wordlist = re.split(delimf, tline)
                        wordlist_colons = re.split(delimc,tline)
                        if (wordlist_colons[10]=='mm'and wordlist_colons[8]=='rtmmea'):
                            mov_value = wordlist_colons[9] # absolute value of pump motor position
                            time_value = wordlist[2]
                            term_accum += mov_value +' '
                            time_accum += time_value +' '
                    term_accum = term_accum[0:-1] #remove trailing space
                    time_accum = time_accum[0:-1]
                    try:
                        Data3.loc[row,kk]           =U32K(term_accum)
                        Data3.loc[row,(kk+'_cnt')]  =len(tempList)
                        Data3.loc[row,(kk+'TS')]    =U32K(time_accum)
                    except ValueError:
                        print('Problem with '+kk+' record')  
        #------------------------------------------------------------------------
                elif findcode == 19: 
                # Collect multiple lines with pump notify(absolute coord) data following search term, combine them 
                # comma delimitted into one entry that will be parsed when plotted. 
                #Collect and store their corresponding timestamps for timing plots of critical operations.
                    tempList=GetLinesWith(txt2find)  # get all the lines with search term
                    term_accum =''
                    time_accum =''
                    mov_value =''
                    time_value=''
                    for tl, tline in enumerate(tempList): #Find these terms in these lines and value that follows
                        wordlist_colon = re.split(delimc, tline)                       
                        wordlist = re.split(delimf, tline)
                        try:
                            mov_value  = wordlist_colon[(wordlist_colon.index('rtmmea')+1)]
                        except ValueError: # if its anything else, don't record it
                            continue
                        time_value = str(wordlist[2])
                        term_accum += str(mov_value)+' '
                        time_accum += time_value+' '
                    term_accum=term_accum[0:-1] #remove trailing space
                    time_accum = time_accum[0:-1]
                    try:
                        Data3.loc[row,kk]           =U32K(term_accum)
                        Data3.loc[row,(kk+'_cnt')]  =len(tempList)
                        Data3.loc[row,(kk+'TS')]    =U32K(time_accum)
                    except ValueError:
                        print('Problem with '+kk+' record') 
        #------------------------------------------------------------------------
                elif findcode == 20: 
                # Collect multiple lines with pump notify(absolute coord) data following search term, combine them 
                # comma delimitted into one entry that will be parsed when plotted. 
                #Collect and store their corresponding timestamps for timing plots of critical operations.
                    tempList=GetLinesWith(txt2find)  # get all the lines with search term
                    term_accum =''
                    time_accum =''
                    for tl, tline in enumerate(tempList): #Find these terms in these lines and value that follows
                        wordlist_c = re.split(delimc, tline)
                        wordlistf = re.split(delimf,tline)
                        try:
                            mov_value  = wordlist_c[(wordlist_c.index('Pressure')+2)]
                        except ValueError: # if its anything else, don't record it
                            continue
                        time_value = str(wordlistf[2])
                        term_accum += str(mov_value)+' '
                        time_accum += str(time_value)+' '
                    term_accum=term_accum[0:-1] #remove trailing space
                    time_accum = time_accum[0:-1]
                    try:
                        Data3.loc[row,kk]           =U32K(term_accum)
                        Data3.loc[row,(kk+'_cnt')]  =len(tempList)
                        Data3.loc[row,(kk+'TS')]    =U32K(time_accum)
                    except ValueError:
                        print('Problem with '+kk+' record') 
                #-----------------------------------------------------------------------------
                elif findcode==21: #targets and selected object tracking data                    
                    tempList=GetLinesWith(txt2find)                    
                    Error='';
                    for jj, line2decode in enumerate(tempList): #collect all ERROR lines
                        wordlist = re.split(':', line2decode)
                        temp= wordlist[(wordlist.index('ERROR')+1)]
                        temp=temp.replace(' ','_') # replace spaces with underbars
                        Error += temp+' '
                    Data3.loc[row,'ERROR']  =Error[0:-1]
                    Data3.loc[row,'ERROR_Count']  =str(len(tempList))
                        
        Data3.loc[row,'Sample_Type']=specimenCat
        # save as you go should let you startup where you left of if interrupted.
                     
        # INCREMENT main index
        row +=1
        fi.close # close all the log files you opened
        #end the for loops searching logs and directories

#---------------------------------------------------------------------------------------------
# Data is all acquired in Pandas Data frame now and written out.
try:
    outfile = open(PathPlusName, 'wb')
    Data3.to_csv(PathPlusName,index=False)
    outfile.close()
except PermissionError:
    print('Permission denied on ', SavedFileName, ' - Probably in use ')  
DFTemp = pd.DataFrame()  # Temp storage for each barcode's dataframe info

#Generate the list of unique barcodes
Data3[['Bar_Code']]=Data3[['Bar_Code']]
Data3.sort(columns=['Bar_Code'])
Data3.set_index(keys=['Bar_Code'],drop=False,inplace=True)
ListofBarCodes = Data3.Bar_Code.unique().tolist()
Data3 = Data3.reset_index(drop=True)

# Now write files as individual barcode files.
for BCx in ListofBarCodes:
    #filedate=Data3.
    savedfileBC = pth1+'\\'+SavedFileName+'_BC_'+str(BCx)+'.csv'
    DFTemp = Data3.loc[Data3.Bar_Code==BCx]
    try:
        DFTemp.to_csv(savedfileBC, index=False)
    except PermissionError:
        print('Permission denied on ', str(savedfileBC))

t1 = dt.datetime.now()
deltaT = t1-t0
time_difference_in_minutes = deltaT/dt.timedelta(minutes=1)
filerate = row/(time_difference_in_minutes*60)
s = 'Processed {0:d} .log files in {1:5.2f} minutes or {2:6.3f} .log files per sec'.format(row,time_difference_in_minutes,filerate)
print(s)
print()