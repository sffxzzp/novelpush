import json, os
from urllib.parse import quote, unquote
from zutils.web import weblib
from zutils.file import filelib

class my716:
	def __init__(self, pluginmanager):
		self.pluginmanager = pluginmanager
		self.enabled = True
		self.debug = True
		self.id = 0
		self.name = self.__class__.__name__
		self.hasCover = False
		self.chapters = []
		self.url = 'http://book.my716.com/'
		self.searchurl = 'https://api.zhuishushenqi.com/book/fuzzy-search?query=%s'
		self.sourceurl = 'https://api.zhuishushenqi.com/atoc?view=summary&book=%s'
		self.infourl = 'https://api.zhuishushenqi.com/book/%s'
		self.cataurl = 'https://api.zhuishushenqi.com/atoc/%s?view=chapters'
		self.chapterurl = 'https://chapterup.zhuishushenqi.com/chapter/%s'
		self.filecont = '<?xml version="1.0" encoding="utf-8"?>\n<html xmlns=\"http://www.w3.org/1999/xhtml\">\n<head>\n<title>%(title)s</title>\n<link href=\"stylesheet.css\" rel=\"stylesheet\" type=\"text/css\"/>\n</head>\n<body>\n<h2 class=\"center\">%(title)s</h2><hr>\n<div id=\"content\"><p>%(content)s</p></div>\n</body>\n</html>'
	def search(self, keyword):
		scont = json.loads(weblib().get(self.searchurl % quote(keyword)), True)
		self.sresult = []
		if scont['ok']:
			bcount = 10 if scont['total'] > 10 else scont['total']
			scont = scont['books']
			for i in range(0, bcount):
				self.sresult.append({'id': scont[i]['_id'], 'title': scont[i]['title'], 'url': scont[i]['_id'], 'author': scont[i]['author']})
			return self.sresult
	def getsid(self, bid):
		sources = json.loads(weblib().get(self.sourceurl % bid), True)
		for source in sources:
			if source['source'] == 'xbiquge':
				return source['_id']
	def getInfo(self, selection):
		self.selection = selection
		book = self.sresult[self.selection]
		icont = json.loads(weblib().get(self.infourl % book['url']), True)
		book['cover'] = unquote(icont['cover'][7:-3])
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
		book['url'] = self.cataurl % self.getsid(book['id'])
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
			content = '　　%s' % ccont['chapter']['body'].replace('\n', '<br />　　')
		else:
			content = ''
		fn = '%d.html' % (i+1)
		filelib().write('%s/%s' % (self.path, fn), self.filecont % {'title': cinfo['title'], 'content': content}, encoding='utf-8')

def getClass(pluginmanager):
	return my716(pluginmanager)