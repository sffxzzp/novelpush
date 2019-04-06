import re

def findstr(rule, string):
	findstr = re.compile(rule)
	return findstr.findall(string)