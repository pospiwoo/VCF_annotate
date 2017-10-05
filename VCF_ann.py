import os, sys, time
import urllib3
from datetime import timedelta
from collections import defaultdict

class annotateVCF:
	def __init__(self, file_name, out_file_name):
		# initialize IO files and global variables
		self.inFile = open(file_name,'r')
		self.outFile = open(out_file_name,'w')
		self.TYPE_cnt = defaultdict(int)
		self.http = urllib3.PoolManager()
		self.query_str = ""


    	def __del__(self):
		# close all open files in destruct
		self.inFile.close()
		self.outFile.close()


	def execution_time(func): # timer decorator
		def wrapper(*args, **kwargs):
			begin = time.time()
			func(*args, **kwargs)
			finish = time.time()
			time_in_sec = finish - begin
			print 'Excecution time:', str(timedelta(seconds=time_in_sec))
		return wrapper


    	@execution_time
	def process(self):
		for line in self.inFile:
			if line.startswith("#"): #skip header lines
				continue
			data = line.strip().split("\t")
			if len(data) < 11: #skip insufficient lines
				continue
			CHROM = data[0]
			POS = data[1]
			ID = data[2]
			REF = data[3]
			ALT = data[4]
			QUAL = data[5]
			FILTER = data[6]
			INFO = data[7]
			FORMAT = data[8]

			# parsing annotation info from INFO string
			answer1, answer2, answer3, answer4 \
				= self.infoProcess(INFO)

			# making query string and get data from URL
			self.makeQuery(CHROM, POS, REF, ALT)
			answer5, answer6 = self.getUrlRequest()

			# write annotations to output file
			self.writeToFile(line, answer1, answer2, answer3, \
				answer4, answer5, answer6)


	def makeQuery(self, CHROM, POS, REF, ALT): # func for making URL query
		self.query_str = "http://exac.hms.harvard.edu/rest/variant/variant/"
		self.query_str += CHROM + "-"
		self.query_str += POS + "-"
		self.query_str += REF + "-"
		self.query_str += ALT


	def getUrlRequest(self): # get results from the query
		r = self.http.request('GET', self.query_str)
		if "allele_freq" not in r.data:
			return "NA", r.data
		returned = r.data.replace("{\"","").replace("\"}","").split(", \"")
		for i in xrange(len(returned)):
			tuple_data = returned[i].split("\": ")
			if tuple_data[0] == "allele_freq":
				allele_freq = tuple_data[1]
		return allele_freq, r.data


	def infoProcess(self, INFO): # parse INFO string and get annotation information
		info_list = INFO.split(";")
		for i in info_list:
			if i.startswith("TYPE="):
				self.TYPE_cnt[i]  += 1
				type_str = i.split("=")[1]
				if type_str.find(",") > -1:
					type_str = type_str.split(",")[0]
			if i.startswith("DP="):
				r_depth = i.split("=")[1]
			if i.startswith("AO="):
				allele_o = i.split("=")[1]
				if allele_o.find(",") > -1:
					allele_o = allele_o.split(",")[0]
			if i.startswith("RO="):
				ref_o = i.split("=")[1]
				if ref_o.find(",") > -1:
					ref_o = ref_o.split(",")[0]
		a_5 = float(allele_o) / float(r_depth) * 100
		a_6 = float(ref_o) / float(r_depth) * 100	
		return type_str, r_depth, allele_o, a_6


	def writeToFile(self, line, answer1, answer2, answer3, answer4, answer5, answer6):
		write_str = ""
		write_str += line.strip() + "\t"
		write_str += str(answer1) + "\t"
		write_str += str(answer2) + "\t"
		write_str += str(answer3) + "\t"
		write_str += str(answer4) + "\t"
		write_str += str(answer5) + "\t"
		write_str += str(answer6) + "\n"
		self.outFile.write(write_str)


if __name__ == "__main__":
	help_message = \
	"""
	*********************************************************
	* This script requires two arguments.                   *
	* usage : VCF_ann.py <input_VCF_file> <output_VCF_file> *
	*********************************************************
	"""
	# print help
	if len(sys.argv) < 3 or \
		"-h" in sys.argv or \
		"-H" in sys.argv or \
		"--help" in sys.argv or \
		"--HELP" in sys.argv:
		print help_message
		exit()

	# get IO file names from args
	file_name = sys.argv[1]
	o_file_name = sys.argv[2]

	# init instance and run driver functions
	annVCF_obj = annotateVCF(file_name, o_file_name)
	annVCF_obj.process()
	del annVCF_obj

