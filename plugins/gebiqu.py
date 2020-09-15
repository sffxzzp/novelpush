import json, os, re
from urllib.parse import quote, unquote
from zutils.web import weblib
from zutils.string import findstr
from zutils.file import filelib

class gebiqu:
	def __init__(self, pluginmanager):
		self.pluginmanager = pluginmanager
		self.enabled = True
		self.debug = True
		self.id = 0
		self.name = self.__class__.__name__
		self.hasCover = False
		self.chapters = []
		self.url = 'http://www.gebiqu.com/'
		self.searchurl = 'http://www.gebiqu.com/modules/article/search.php?searchkey=%s'
		self.cataurl = 'http://www.gebiqu.com/biquge_%s/'
		self.chapterurl = 'http://www.gebiqu.com%s'
		self.filecont = '<?xml version="1.0" encoding="utf-8"?>\n<html xmlns=\"http://www.w3.org/1999/xhtml\">\n<head>\n<title>%(title)s</title>\n<link href=\"stylesheet.css\" rel=\"stylesheet\" type=\"text/css\"/>\n</head>\n<body>\n<h2 class=\"center\">%(title)s</h2><hr>\n<div id=\"content\"><p>%(content)s</p></div>\n</body>\n</html>'
	def search(self, keyword):
		scont = weblib().get(self.searchurl % quote(keyword), chardet=True)
		results = findstr('<tr id="nr">[\s\S]*?</tr>', scont)
		self.sresult = []
		for result in results:
			rid, title = findstr('<td class="odd"><a href=".*?/txt/(\d*).html">(.*?)</a></td>', result)[0]
			author = findstr('<td class="odd">([^<>]*?)</td>', result)[0]
			self.sresult.append({'id': rid, 'title': title, 'url': 'http://www.gebiqu.com/biquge_%s/' % rid, 'author': author})
		return self.sresult
	def getInfo(self, selection):
		self.selection = selection
		book = self.sresult[self.selection]
		icont = weblib().get(book['url'], chardet=True)
		book['cover'] = findstr('<div id="fmimg"><img.*src="(.*?\d*/.*?\.jpg)" ?/?><span class="b">', icont)[0]
		book['time'] = findstr('<p>最后更新：(.*?)</p>', icont)[0]
		book['last'] = ''
		book['des'] = findstr('<div id="intro"><p>([\s\S]*?)<a href="https?://down.*?".*?>.*?</a></p></div>', icont)[0]
		return book
	def checkStart(self):
		self.path = 'books/%s/%s' % (self.name, self.sresult[self.selection]['id'])
		if not filelib().exists(self.path):
			filelib().mkdir(self.path)
		count = 0
		for filename in os.listdir(self.path):
			if filename.endswith('html') and filename != 'titlepage.html':
				count += 1
			elif filename == 'cover.jpg':
				self.hasCover = True
		return count
	def getCata(self):
		book = self.sresult[self.selection]
		book['url'] = self.cataurl % book['id']
		cinfo = weblib().get(book['url'], chardet=True)
		cinfo = findstr('<div id="list"><dl><dt>[\s\S]*</dt>([\s\S]*?)</dl></div>', cinfo)[0]
		chapters = findstr('<dd><a href="(/biquge_\d*/\d*.html)">(.*?)</a></dd>', cinfo)
		for chapter in chapters:
			url, title = chapter
			self.chapters.append({'title': title, 'url': self.chapterurl % url})
		return self.chapters
	def download(self, start):
		for i in range(start, len(self.chapters)):
			self.downChap(i)
		if not self.hasCover:
			weblib().download(self.sresult[self.selection]['cover'], '%s/cover.jpg' % self.path)
		return self.path
	def downChap(self, i):
		cinfo = self.chapters[i]
		print('\t%s' % cinfo['title'].encode('gbk', 'ignore').decode('gbk'))
		ccont = weblib().get(cinfo['url'], chardet=True)
		try:
			content = findstr('<div id="content">([\s\S]*?)</div>', ccont)[0].replace('&nbsp;', '').replace('  ', '').replace('www.gebiqu.com', '')
			content = re.sub('<br ?/?><br ?/?>', '<br />　　', content)
		except:
			content = ''
		fn = '%d.html' % (i+1)
		filelib().write('%s/%s' % (self.path, fn), self.filecont % {'title': cinfo['title'], 'content': content}, encoding='utf-8')

def getClass(pluginmanager):
	return gebiqu(pluginmanager)