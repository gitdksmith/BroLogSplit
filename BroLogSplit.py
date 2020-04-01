#!/usr/bin/python

# Script to split bro logs into gzip files by date.
# New files format: <inputFileName>-YYYYMMDD.gz

import gzip
import lzma
import time
import sys


def isInt(x):
	'''
	Returns True of string can be parsed as an int, False otherwise.
	'''
	try: 
		int(x)
		return True
	except ValueError:
		return False


def usage():
	print "Purpose: Split bro logs into gzip files by date.\n"
	print "Usage:"
	print "\t$ ./split_brolog.py <filename> [<YYYYMMDD>]"
	print "\tfilename\tThe bro log to split. Can be regular, gz, or xz file."
	print "\tYYYYMMDD\tOPTIONAL timestamp. Tells script what day to start creating output files from."


def checkInputs():
	if len(sys.argv) < 2 or '-h' in sys.argv:
		usage()
		exit()


def checkTimestamp():
	'''
	Get timestamp from command line arguments.
	Timestamp will be used as starting point for reading log file.
	'''
	startDay = None
	if len(sys.argv) == 3:
		startDay = sys.argv[2]
		if len(startDay) != 8 or not isInt(startDay):
			print "Error: Malformed timestamp"
			usage()
			exit()
	return startDay
	

def writeAndReset(buff, cnt, writefile):
	'''
	Join all strings in buffer and write to file.
	'''
	writefile.write(''.join(x for x in buff))
	return list(), 0


def getFileHandle(inputFile):
	'''
	Support gz, xz, and regular files
	'''
	f = None
	try:
		f = gzip.open(inputFile, 'r')
		f._read_gzip_header()
		f.rewind()
	except:
		f.close()
		try:
			f = lzma.LZMAFile(inputFile)
			f.readline()
			f.seek(0)
		except:
			f.close()
			f = open(inputFile, 'r')
	
	return f

def splitFile(inputFile, startDay):
	'''
	Loop over input file, start new output file for each new day.
	'''
	# buffer the lines to call write fewer times
	buffSize = 5000
	buff = list()

	prevYMD = "-1"
	writefile = None
	header = "";
	fileList = list()
	cnt = 0

	# open file
	f = getFileHandle(inputFile)
	if f is None:
		print "Could not open file", inputFile
		exit()

	outputFileName = inputFile
	if inputFile.endswith('.gz') or inputFile.endswith('.xz'):
		outputFileName = inputFile[:-3]


	# will read line by line and not load into memory.
	for line in f:
		line = line.rstrip()
		if line:
			if line[0] == '#':
				header += line + "\n"
				continue

			# 1495135849.059179  CIxL8k2khdqate30kg  srcip  65204 dstip  8600  tcp   -   0.006308 0  0  REJ  T  F  0  Sr  2  96  2  80  (empty)
			splits = line.split()

			try:
				epoch = float(splits[0])
			except:
				print "skipping malfomed line:", line
				continue
	
			# time.struct_time(tm_year=2017, tm_mon=5, tm_mday=22, tm_hour=21, tm_min=35, tm_sec=15, tm_wday=0, tm_yday=142, tm_isdst=0)
			gmt = time.gmtime(epoch)
			currentYMD = str(gmt.tm_year) + str(gmt.tm_mon).zfill(2) + str(gmt.tm_mday).zfill(2)

			# If defined, continue until we get to startDay
			if startDay is not None and int(currentYMD) < int(startDay):
				continue

			if int(currentYMD) != int(prevYMD):
				# Keep track of files we created during this run.
				# ONLY append to those we created, otherwise overwrite old files.
				# new file needs to be created.

				if writefile is not None:
					# Write closing line with last timestamp
					#close  2017-05-23-19-29-17
					#writefile.write("#close "+str(year)+"-"+str(month).zfill(2)+"-"+str(day).zfill(2)+"-"+str(gmt.tm_hour).zfill(2)+"-"+str(gmt.tm_min).zfill(2)+"-"+str(gmt.tm_sec).zfill(2)+"\n")
					buff, cnt = writeAndReset(buff, cnt, writefile)
					writefile.close()

				newFile = outputFileName + "-" + currentYMD + ".gz"
				if newFile in fileList:
					print "appending to file for date", currentYMD
					writefile = gzip.open(newFile, 'ab')
				else:
					print "creating file for date", currentYMD
					writefile = gzip.open(newFile, 'wb')
					fileList.append(newFile)
					writefile.write(header);

				prevYMD = currentYMD
			
			buff.append(line+"\n")
			cnt += 1
			if cnt > buffSize:
				buff, cnt = writeAndReset(buff, cnt, writefile)
			

	#writefile.write("#close "+str(year)+"-"+str(month).zfill(2)+"-"+str(day).zfill(2)+"-"+str(gmt.tm_hour).zfill(2)+"-"+str(gmt.tm_min).zfill(2)+"-"+str(gmt.tm_sec).zfill(2)+"\n")
	writefile.write(''.join(x for x in buff))
	writefile.close()

	f.close()


def main():
	checkInputs()
	inputFile = sys.argv[1]
	startDay = checkTimestamp()
	
	print "Using input file:", inputFile
	splitFile(inputFile, startDay)


if __name__ == "__main__":
	main()

