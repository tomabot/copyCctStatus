#!/usr/local/env ruby
require 'json'

#
# CopyCalImages
#
def CopyCalImages(cctname, cctip, timestamp)
	puts "( #{cctname} ) ...Copying calibration images..."
	year, month, day = timestamp.strftime("%Y %m %d").split()
	ymd = year + month + day

		srcdir = "/var/local/cellct/#{cctname}"
		dstdir = "/mnt/lancer/upload/DailyInstrumentData/#{cctname}/calibImages/#{ymd}"

		begin
			puts "mkdir #{dstdir}"
			`mkdir #{dstdir}`
			puts "ssh cctuser@#{cctip} \"cd #{srcdir}/DS* ; tar -zcf - *\" | (cd #{dstdir} ; tar zxf -)"
			     `ssh cctuser@#{cctip} \"cd #{srcdir}/DS* ; tar -zcf - *\" | (cd #{dstdir} ; tar zxf -)`
			if $?.exitstatus != 0
				raise Exception, "ssh failed"
			end
			rescue Exception => e
				puts "copyCalImages( #{cctname} ): #{e.message}"
			end
end

#
# CopyRtmLogs
#
def CopyRtmLogs(cctname, cctip, timestamp)
	puts "( #{cctname} ) ...Copying rtm logs..."
	year, month, day = timestamp.strftime("%Y %m %d").split()
	ymd = year + month + day
	dateSearchStr = timestamp.strftime("%b %e")

	dstdir  = "/mnt/lancer/upload/DailyInstrumentData/#{cctname}/gservlog/rtm"
	srcfile = "rtm_#{ymd}"

	begin
        puts "ssh cctuser@#{cctip} \"grep \'#{dateSearchStr}\' /var/log/gservlog/rtm* > /home/cctuser/#{srcfile} \""
             `ssh cctuser@#{cctip} \"grep \'#{dateSearchStr}\' /var/log/gservlog/rtm* > /home/cctuser/#{srcfile} \"`
        if $?.exitstatus != 0
            raise Exception, "first ssh failed"
        end

		puts "ssh cctuser@#{cctip} \"tar -zcf - #{srcfile} \" | (cd #{dstdir} ; tar zxf -)"
		     `ssh cctuser@#{cctip} \"tar -zcf - #{srcfile} \" | (cd #{dstdir} ; tar zxf -)`
		if $?.exitstatus != 0
			raise Exception, "second ssh failed"
		end

	rescue Exception => e
		puts "copyRtmLogs( #{cctname} ): #{e.message}"
	end
end	

#
# CopyUcmStatus
#
def CopyUcmStatus(cctname, cctip, timestamp)
	puts "( #{cctname} ) ...Copying ucm status..."
	year, month, day = timestamp.strftime("%Y %m %d").split()
	ymd = year + month + day
	ym = year + month

	srcdir = "/var/log/gservlog"
	dstdir = "/mnt/lancer/upload/DailyInstrumentData/#{cctname}/gservlog"

	begin
		puts "scp -p -r cctuser@#{cctip}:#{srcdir}/ucmstatus/ucm_status-#{ymd} #{dstdir}/daily_ucm_status"
		     `scp -p -r cctuser@#{cctip}:#{srcdir}/ucmstatus/ucm_status-#{ymd} #{dstdir}/daily_ucm_status`
		if $?.exitstatus != 0
			raise Exception, "scp failed"
		end

		puts "ssh cctuser@#{cctip} \"cd #{srcdir}/ucm/#{cctname}_#{ym};tar zcf - #{day}\" | (cd #{dstdir}/ucm_logs/#{cctname}_#{ym};tar zxf - )"
		     `ssh cctuser@#{cctip} \"cd #{srcdir}/ucm/#{cctname}_#{ym};tar zcf - #{day}\" | (cd #{dstdir}/ucm_logs/#{cctname}_#{ym};tar zxf - )`
		if $?.exitstatus != 0
			raise Exception, "ssh failed"
		end
	rescue Exception => e
		puts "CopyUcmStatus( #{cctname} ): #{e.message}"
	end
end

#
# execution starts here
#
if ARGV[0] == nil
	configFile = "/home/tomabot/local/src/copyCctStatus/cct_config"
else
	configFile = ARGV[0]
end

cctConfig = File.read( "#{configFile}" )
cctJson = JSON.parse( cctConfig )
cctJson.each do |cctname, cctip|
	timestamp = Time.now() - 86400.0
	CopyCalImages(cctname, cctip, timestamp)
	CopyRtmLogs(cctname, cctip, timestamp)
	CopyUcmStatus(cctname, cctip, timestamp)
end


