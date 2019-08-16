import json, os
from urllib.parse import quote, unquote
from zutils.web import weblib
from zutils.file import filelib

class gdugm:
	def __init__(self, pluginmanager):
		self.pluginmanager = pluginmanager
		self.enabled = True
		self.debug = True
		self.id = 0
		self.name = self.__class__.__name__
		self.hasCover = False
		self.chapters = []
		self.url = 'http://lunbo.gdudm.cn/'
		self.searchurl = 'http://lunbo.gdugm.cn/book/search?key=%s&start=0&limit=100'
		self.infourl = 'http://api.gdugm.cn/book/info?bookId=%s'
		self.cataurl = 'http://api.gdugm.cn/toc/mix?bookId=%s'
		self.chapterurl = 'http://chapter.gdugm.cn/chapter/%s'
		self.filecont = '<?xml version="1.0" encoding="utf-8"?>\n<html xmlns=\"http://www.w3.org/1999/xhtml\">\n<head>\n<title>%(title)s</title>\n<link href=\"stylesheet.css\" rel=\"stylesheet\" type=\"text/css\"/>\n</head>\n<body>\n<h2 class=\"center\">%(title)s</h2><hr>\n<div id=\"content\"><p>%(content)s</p></div>\n</body>\n</html>'
	def search(self, keyword):
		scont = json.loads(weblib().get(self.searchurl % quote(keyword)), True)
		self.sresult = []
		if scont['ok']:
			scont = scont['books']
			bcount = 10 if len(scont) > 10 else len(scont)
			for i in range(0, bcount):
				self.sresult.append({'id': scont[i]['_id'], 'title': scont[i]['title'], 'url': scont[i]['_id'], 'author': scont[i]['author']})
			return self.sresult
	def getInfo(self, selection):
		self.selection = selection
		book = self.sresult[self.selection]
		icont = json.loads(weblib().get(self.infourl % book['url']), True)
		book['cover'] = icont['cover']
		book['time'] = ' '.join(icont['updated'].split('.')[0].split('T'))
		book['last'] = icont['lastChapter']
		book['des'] = icont['longIntro']
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
		cinfo = json.loads(weblib().get(book['url']), True)
		for chapter in cinfo['chapters']:
			self.chapters.append({'title': chapter['title'], 'url': self.chapterurl % quote(chapter['link'])})
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
		ccont = json.loads(weblib().get(cinfo['url']), True)
		if ccont['ok'] == True:
			content = '　　%s' % ccont['chapter']['body'].replace('　', '').replace('\n', '<br />　　')
		else:
			content = ''
		fn = '%d.html' % (i+1)
		filelib().write('%s/%s' % (self.path, fn), self.filecont % {'title': cinfo['title'], 'content': content}, encoding='utf-8')

def getClass(pluginmanager):
	return gdugm(pluginmanager)