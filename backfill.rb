#!/usr/local/env ruby
require 'json'

#
# CopyCalImages
#
def CopyCalImages(cctname, cctip, timestamp, debug)
    puts "\n( #{cctname} ) ...Copying calibration images..."

    year, month, day = timestamp.strftime("%Y %m %d").split()
    ymd = year + month + day

    srcdir = "/var/local/cellct/#{cctname}"
    dstdir = "/mnt/lancer/upload/DailyInstrumentData/#{cctname}/calibImages/#{ymd}"

    puts "mkdir #{dstdir}"
    if debug == "false"
        `mkdir #{dstdir}`
        if $?.exitstatus != 0
            puts "...mkdir failed in CopyCalImages... continuing"
        end
    end

    puts "ssh cctuser@#{cctip} \"cd #{srcdir}/DS* ; tar -zcf - *\" | (cd #{dstdir} ; tar zxf -)"
    if debug == "false"
        `ssh cctuser@#{cctip} \"cd #{srcdir}/DS* ; tar -zcf - *\" | (cd #{dstdir} ; tar zxf -)`
        #if $?.exitstatus != 0
        #    puts "...ssh failed in CopyCalImages... continuing"
        #end
    end
end

#
# CopyCameractlLogs
#
def CopyCameractlLogs(cctname, cctip, timestamp, debug)
    puts "\n( #{cctname} ) ...Copying cameractl logs..."

    year, month, day = timestamp.strftime("%Y %m %d").split()
    ymd = year + month + day

    srcdir = "/var/log/gservlog"
    srcfile = "cameractl"
    srcfile_ymd = "cameractl-#{ymd}"

    dstdir  = "/mnt/lancer/upload/DailyInstrumentData/#{cctname}/gservlog/cameractl"

    puts "ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile} \" | (cd #{dstdir} ; tar zxf -)"
    if debug == "false"
        `ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile} \" | (cd #{dstdir} ; tar zxf -)`
        #if $?.exitstatus != 0
        #    puts "...first ssh failed in CopyCameractlLogs... continuing"
        #end
    end

    puts "ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile_ymd} \" | (cd #{dstdir} ; tar zxf -)"
    if debug == "false"
        `ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile_ymd} \" | (cd #{dstdir} ; tar zxf -)`
        #if $?.exitstatus != 0
        #    puts "...second ssh failed in CopyCameractlLogs... continuing"
        #end
    end
end

#
# CopyHpiLogs
#
def CopyHpiLogs(cctname, cctip, timestamp, debug)
    puts "\n( #{cctname} ) ...Copying hpi logs..."

    year, month, day = timestamp.strftime("%Y %m %d").split()
    ymd = year + month + day

    dstdir  = "/mnt/lancer/upload/DailyInstrumentData/#{cctname}/gservlog/hpi"

    srcdir = "/var/log/gservlog"
    srcfile = "hpi"
    srcfile_ymd = "hpi-#{ymd}"

    puts "ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile} \" | (cd #{dstdir} ; tar zxf -)"
    if debug == "false"
        `ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile} \" | (cd #{dstdir} ; tar zxf -)`
        #if $?.exitstatus != 0
        #    puts "...first ssh failed in CopyHpiLogs... continuing"
        #end
    end

    puts "ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile_ymd} \" | (cd #{dstdir} ; tar zxf -)"
    if debug == "false"
        `ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile_ymd} \" | (cd #{dstdir} ; tar zxf -)`
        #if $?.exitstatus != 0
        #    puts "...second ssh failed in CopyHpiLogs... continuing"
        #end
    end

end

#
# CopyImgprocessdLogs
#
def CopyImgprocessdLogs(cctname, cctip, timestamp, debug)
    puts "\n( #{cctname} ) ...Copying imgprocessd logs..."

    year, month, day = timestamp.strftime("%Y %m %d").split()
    ymd = year + month + day

    dstdir  = "/mnt/lancer/upload/DailyInstrumentData/#{cctname}/gservlog/imgprocessd"

    srcdir = "/var/log/gservlog"
    srcfile = "imgprocessd"
    srcfile_ymd = "imgprocessd-#{ymd}"

    puts "ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile} \" | (cd #{dstdir} ; tar zxf -)"
    if debug == "false"
        `ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile} \" | (cd #{dstdir} ; tar zxf -)`
        #if $?.exitstatus != 0
        #    puts "...first ssh failed in CopyImgprocessdLogs... continuing"
        #end
    end

    puts "ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile_ymd} \" | (cd #{dstdir} ; tar zxf -)"
    if debug == "false"
        `ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile_ymd} \" | (cd #{dstdir} ; tar zxf -)`
        #if $?.exitstatus != 0
        #    puts "...second ssh failed in CopyImgprocessdLogs... continuing"
        #end
    end
end

#
# CopyRtmLogs
#
def CopyRtmLogs(cctname, cctip, timestamp, debug)
    puts "\n( #{cctname} ) ...Copying rtm logs..."

    year, month, day = timestamp.strftime("%Y %m %d").split()
    ymd = year + month + day

    dstdir  = "/mnt/lancer/upload/DailyInstrumentData/#{cctname}/gservlog/rtm"

    srcdir = "/var/log/gservlog"
    srcfile = "rtm"
    srcfile_ymd = "rtm-#{ymd}"

    puts "ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile} \" | (cd #{dstdir} ; tar zxf -)"
    if debug == "false"
        `ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile} \" | (cd #{dstdir} ; tar zxf -)`
        #if $?.exitstatus != 0
        #    puts "...first ssh failed in CopyRtmLogs... continuing"
        #end
    end

    puts "ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile_ymd} \" | (cd #{dstdir} ; tar zxf -)"
    if debug == "false"
        `ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile_ymd} \" | (cd #{dstdir} ; tar zxf -)`
        #if $?.exitstatus != 0
        #    puts "...second ssh failed in CopyRtmLogs... continuing"
        #end
    end
end

#
# CopySpanLogs
#
def CopySpanLogs(cctname, cctip, timestamp, debug)
    puts "\n( #{cctname} ) ...Copying span logs..."

    year, month, day = timestamp.strftime("%Y %m %d").split()
    ymd = year + month + day

    dstdir_ext  = "/mnt/lancer/upload/DailyInstrumentData/#{cctname}/gservlog/span_http_ext"
    dstdir_int  = "/mnt/lancer/upload/DailyInstrumentData/#{cctname}/gservlog/span_http_int"

    srcdir = "/var/log/gservlog"
    srcfile_ext = "span_http_ext"
    srcfile_ext_ymd = "span_http_ext-#{ymd}"
    srcfile_int = "span_http_int"
    srcfile_int_ymd = "span_http_int-#{ymd}"

    puts "ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile_ext} \" | (cd #{dstdir_ext} ; tar zxf -)"
    if debug == "false"
        `ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile_ext} \" | (cd #{dstdir_ext} ; tar zxf -)`
        #if $?.exitstatus != 0
        #    puts "...first ssh failed in CopySpanLogs... continuing"
        #end
    end

    puts "ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile_ext_ymd} \" | (cd #{dstdir_ext} ; tar zxf -)"
    if debug == "false"
        `ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile_ext_ymd} \" | (cd #{dstdir_ext} ; tar zxf -)`
        #if $?.exitstatus != 0
        #    puts "...second ssh failed in CopySpanLogs... continuing"
        #end
    end

    puts "ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile_int} \" | (cd #{dstdir_int} ; tar zxf -)"
    if debug == "false"
        `ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile_int} \" | (cd #{dstdir_int} ; tar zxf -)`
        #if $?.exitstatus != 0
        #    puts "...third ssh failed in CopySpanLogs... continuing"
        #end
    end

    puts "ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile_int_ymd} \" | (cd #{dstdir_int} ; tar zxf -)"
    if debug == "false"
        `ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile_int_ymd} \" | (cd #{dstdir_int} ; tar zxf -)`
        #if $?.exitstatus != 0
        #    puts "...fourth ssh failed in CopySpanLogs... continuing"
        #end
    end
end

#
# CopyTemperatureMon
#
def CopyTemperatureMon(cctname, cctip, timestamp, debug)
    puts "\n( #{cctname} ) ...Copying temperaturemon..."

    year, month, day = timestamp.strftime("%Y %m %d").split()
    ymd = year + month + day
    ym = year + month

    srcdir = "/var/log/gservlog"
    srcfile = "temperaturemon"

    dstdir = "/mnt/lancer/upload/DailyInstrumentData/#{cctname}/gservlog/temperaturemon"

    puts "ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile} \" | (cd #{dstdir} ; tar zxf -)"
    if debug == "false"
        `ssh cctuser@#{cctip} \"cd #{srcdir} ; tar -zcf - #{srcfile} \" | (cd #{dstdir} ; tar zxf -)`
        if $?.exitstatus != 0
            puts "...ssh failed in CopyTemperatureMon... continuing"
        else
            puts "cd #{dstdir} ; mv #{srcfile} #{srcfile}-#{ymd}"
                 `cd #{dstdir} ; mv #{srcfile} #{srcfile}-#{ymd}`
            if $?.exitstatus != 0
                puts "...cd;mv failed in CopyTemperatureMon... continuing"
            end
        end
    else
        puts "cd #{dstdir} ; mv #{srcfile} #{srcfile}-#{ymd}"
    end
end


#
# CopyUcmLogs
#
def CopyUcmLogs(cctname, cctip, timestamp, debug)
    puts "\n( #{cctname} ) ...Copying ucm logs..."

    year, month, day = timestamp.strftime("%Y %m %d").split()
    ymd = year + month + day
    ym = year + month

    srcdir = "/var/log/gservlog/ucm/#{cctname}_#{ym}"
    dstdir = "/mnt/lancer/upload/DailyInstrumentData/#{cctname}/gservlog/ucm_logs/#{cctname}_#{ym}"

    puts "ssh cctuser@#{cctip} \"cd #{srcdir} ; tar zcf - #{day}\" | (cd #{dstdir} ; tar zxf - )"
    if debug == "false"
        `ssh cctuser@#{cctip} \"cd #{srcdir} ; tar zcf - #{day}\" | (cd #{dstdir} ; tar zxf - )`
	#if $?.exitstatus != 0
        #    puts "...ssh failed in CopyUcmLogs... continuing"
        #end
    end
end

#
# CopyUcmStatus
#
def CopyUcmStatus(cctname, cctip, timestamp, debug)
    puts "\n( #{cctname} ) ...Copying ucm status..."

    year, month, day = timestamp.strftime("%Y %m %d").split()
    ymd = year + month + day
    ym = year + month

    srcdir = "/var/log/gservlog"
    srcfile = "ucm_status-#{ymd}"

    dstdir = "/mnt/lancer/upload/DailyInstrumentData/#{cctname}/gservlog/daily_ucm_status"

    puts "ssh cctuser@#{cctip} \"cd #{srcdir}/ucmstatus ; tar -zcf - #{srcfile} \" | (cd #{dstdir} ; tar zxf -)"
    if debug == "false"
        `ssh cctuser@#{cctip} \"cd #{srcdir}/ucmstatus ; tar -zcf - #{srcfile} \" | (cd #{dstdir} ; tar zxf -)`
        #if $?.exitstatus != 0
        #    puts "...ssh failed in CopyUcmStatus... continuing"
        #end
    end
end

#
# execution starts here
#
debug = "false"

if ARGV[0] == nil
    configFile = "/home/vguser/local/src/copyCctStatus/cct_config"
else
    configFile = ARGV[0]
end

cctConfig = File.read( "#{configFile}" )
cctJson = JSON.parse( cctConfig )
cctJson.each do |cctname, cctip|
    # set timestamp to yesterday (rightnow - 24hrs)
    timestamp = Time.now() - ( 86400.0 * 6 )

    CopyCalImages(cctname, cctip, timestamp, debug)
    CopyCameractlLogs(cctname, cctip, timestamp, debug)
    CopyHpiLogs(cctname, cctip, timestamp, debug)
    CopyImgprocessdLogs(cctname, cctip, timestamp, debug)
    CopyRtmLogs(cctname, cctip, timestamp, debug)
    CopySpanLogs(cctname, cctip, timestamp, debug)
    CopyTemperatureMon(cctname, cctip, timestamp, debug)
    CopyUcmLogs(cctname, cctip, timestamp, debug)
    CopyUcmStatus(cctname, cctip, timestamp, debug)

    puts " "
    # set timestamp to yesterday (rightnow - 24hrs)
    timestamp = Time.now() - ( 86400.0 * 5 )

    CopyCalImages(cctname, cctip, timestamp, debug)
    CopyCameractlLogs(cctname, cctip, timestamp, debug)
    CopyHpiLogs(cctname, cctip, timestamp, debug)
    CopyImgprocessdLogs(cctname, cctip, timestamp, debug)
    CopyRtmLogs(cctname, cctip, timestamp, debug)
    CopySpanLogs(cctname, cctip, timestamp, debug)
    CopyTemperatureMon(cctname, cctip, timestamp, debug)
    CopyUcmLogs(cctname, cctip, timestamp, debug)
    CopyUcmStatus(cctname, cctip, timestamp, debug)

    puts " "
    # set timestamp to yesterday (rightnow - 24hrs)
    timestamp = Time.now() - ( 86400.0 * 4 )

    CopyCalImages(cctname, cctip, timestamp, debug)
    CopyCameractlLogs(cctname, cctip, timestamp, debug)
    CopyHpiLogs(cctname, cctip, timestamp, debug)
    CopyImgprocessdLogs(cctname, cctip, timestamp, debug)
    CopyRtmLogs(cctname, cctip, timestamp, debug)
    CopySpanLogs(cctname, cctip, timestamp, debug)
    CopyTemperatureMon(cctname, cctip, timestamp, debug)
    CopyUcmLogs(cctname, cctip, timestamp, debug)
    CopyUcmStatus(cctname, cctip, timestamp, debug)

    puts " "
    # set timestamp to yesterday (rightnow - 24hrs)
    timestamp = Time.now() - ( 86400.0 * 3 )

    CopyCalImages(cctname, cctip, timestamp, debug)
    CopyCameractlLogs(cctname, cctip, timestamp, debug)
    CopyHpiLogs(cctname, cctip, timestamp, debug)
    CopyImgprocessdLogs(cctname, cctip, timestamp, debug)
    CopyRtmLogs(cctname, cctip, timestamp, debug)
    CopySpanLogs(cctname, cctip, timestamp, debug)
    CopyTemperatureMon(cctname, cctip, timestamp, debug)
    CopyUcmLogs(cctname, cctip, timestamp, debug)
    CopyUcmStatus(cctname, cctip, timestamp, debug)

    puts " "
    # set timestamp to yesterday (rightnow - 24hrs)
    timestamp = Time.now() - ( 86400.0 * 2 )

    CopyCalImages(cctname, cctip, timestamp, debug)
    CopyCameractlLogs(cctname, cctip, timestamp, debug)
    CopyHpiLogs(cctname, cctip, timestamp, debug)
    CopyImgprocessdLogs(cctname, cctip, timestamp, debug)
    CopyRtmLogs(cctname, cctip, timestamp, debug)
    CopySpanLogs(cctname, cctip, timestamp, debug)
    CopyTemperatureMon(cctname, cctip, timestamp, debug)
    CopyUcmLogs(cctname, cctip, timestamp, debug)
    CopyUcmStatus(cctname, cctip, timestamp, debug)

    puts " "
    # set timestamp to yesterday (rightnow - 24hrs)
    timestamp = Time.now() - ( 86400.0 * 1 )

    CopyCalImages(cctname, cctip, timestamp, debug)
    CopyCameractlLogs(cctname, cctip, timestamp, debug)
    CopyHpiLogs(cctname, cctip, timestamp, debug)
    CopyImgprocessdLogs(cctname, cctip, timestamp, debug)
    CopyRtmLogs(cctname, cctip, timestamp, debug)
    CopySpanLogs(cctname, cctip, timestamp, debug)
    CopyTemperatureMon(cctname, cctip, timestamp, debug)
    CopyUcmLogs(cctname, cctip, timestamp, debug)
    CopyUcmStatus(cctname, cctip, timestamp, debug)

    puts " "
    # set timestamp to yesterday (rightnow - 24hrs)
    timestamp = Time.now() - 86400.0

    CopyCalImages(cctname, cctip, timestamp, debug)
    CopyCameractlLogs(cctname, cctip, timestamp, debug)
    CopyHpiLogs(cctname, cctip, timestamp, debug)
    CopyImgprocessdLogs(cctname, cctip, timestamp, debug)
    CopyRtmLogs(cctname, cctip, timestamp, debug)
    CopySpanLogs(cctname, cctip, timestamp, debug)
    CopyTemperatureMon(cctname, cctip, timestamp, debug)
    CopyUcmLogs(cctname, cctip, timestamp, debug)
    CopyUcmStatus(cctname, cctip, timestamp, debug)

    puts " "
end


