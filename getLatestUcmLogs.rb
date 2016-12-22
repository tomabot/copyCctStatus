#!/usr/bin/env ruby
require 'json'


#
# CopyUcmLogs
#
def GetLatestLogs(cctname, cctip, timestamp, debug)
    puts "\n( #{cctname} ) ...getting latest ucm logs..."

    year, month, day = timestamp.strftime("%Y %m %d").split()
    ymd = year + month + day
    ym = year + month

    srcdir = "/var/log/gservlog/ucm/#{cctname}_#{ym}/#{day}"
    #srcdir = "testDir/src"
 
    dstdir = "/mnt/lancer/upload/DailyInstrumentData/#{cctname}/gservlog/ucm_logs/#{cctname}_#{ym}"
    dircreate = `mkdir #{dstdir}`

    dstdir = "#{dstdir}/#{day}"
    dircreate = `mkdir #{dstdir}`

    #dstdir = "testDir/dst"

    #puts "ssh cctuser@#{cctip} \"cd #{srcdir} ; ls -1\""
    if debug == "false"
        # get the list of files in the source directory
        srcLst = `ssh cctuser@#{cctip} \"cd #{srcdir}; ls -1 #{srcdir}\"`.split("\n")

        # get the list of files from the destination directory
        dstLst = `ls -1 #{dstdir}`.split("\n")

	#puts "...srcLst looks like this..."
	#puts srcLst

	#puts "...dstLst looks like this..."
	#puts dstLst

        newLst = Array.new

        # get the list of file names that have not yet been copied
        srcLst.each do |newLog|
            newLst.insert(-1, newLog) unless dstLst.include?( newLog )
        end

        #puts "...new list looks like this..."

        # the last file name added to the list might still be open, so don't include it
	newLst.pop

        if( newLst.length > 0 ) 
            newStr = newLst.join(" ")
            #puts newStr
            `ssh cctuser@#{cctip} \"cd #{srcdir}; tar zcvf - #{newStr}\" | (cd #{dstdir}; tar zxvf -)`
        end
    end
end

#
# execution starts here
#
debug = "false"

configFile = "/home/tomabot/local/copyCctStatus/cct_config"
if ARGV[0] != nil
    configFile = ARGV[0]
end

cctConfig = File.read( "#{configFile}" )
cctJson = JSON.parse( cctConfig )
cctJson.each do |cctname, cctip|
    # set timestamp to rightnow 
    timestamp = Time.now()

    GetLatestLogs(cctname, cctip, timestamp, debug)
    puts "...fini... "
end


