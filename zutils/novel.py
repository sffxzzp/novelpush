import os, re
from urllib.parse import quote
from zutils.string import findstr
from zutils.web import weblib
from zutils.file import filelib

class booklib:
	def __init__(self, name):
		self.enabled = False
		self.debug = True
		self.id = 0
		self.name = name
		self.hasCover = False
		self.chapters = []
		self.url = ''
		self.loadcfg('plugins/'+name+'.json')
	def loadcfg(self, path):
		cfgfile = filelib().json(path)
		try:
			self.enabled = cfgfile['enabled']
		except:
			self.enabled = False
		if self.enabled:
			try:
				self.debug = cfgfile['debug']
				self.url = cfgfile['url']
				self.baseurl = findstr('(http[s]?://.*?)/', self.url)[0]
				self.idrule = cfgfile['idrule']
				self.searchurl = cfgfile['searchurl']
				self.sidrule = cfgfile['sidrule']
				self.stitlerule = cfgfile['stitlerule']
				self.surlrule = cfgfile['surlrule']
				self.sauthorrule = cfgfile['sauthorrule']
				self.coverrule = cfgfile['coverrule']
				self.timerule = cfgfile['timerule']
				self.lastrule = cfgfile['lastrule']
				self.desrule = cfgfile['desrule']
				self.listleft = cfgfile['listleft']
				self.listright = cfgfile['listright']
				self.listrule = cfgfile['listrule']
				self.chaprule = cfgfile['chaprule']
				self.chapclean = cfgfile['chapclean']
				self.chapcleanre = cfgfile['chapcleanre']
				self.output = cfgfile['output']
			except:
				pass
	def search(self, keyword):
		scont = weblib().get(self.searchurl % quote(keyword), chardet=True)
		self.sresult = []
		sids = findstr(self.sidrule, scont)
		stitles = findstr(self.stitlerule, scont)
		surls = findstr(self.surlrule, scont)
		sauthors = findstr(self.sauthorrule, scont)
		for i in range(0, len(stitles)):
			self.sresult.append({'id': sids[i], 'title': stitles[i], 'url': surls[i], 'author': sauthors[i]})
		return self.sresult
	def getInfo(self, selection):
		self.selection = selection
		book = self.sresult[self.selection]
		if not 'http' in book['url']:
			book['url'] = self.baseurl + book['url']
		icont = weblib().get(book['url'], chardet=True)
		if not self.coverrule == '':
			try:
				book['cover'] = findstr(self.coverrule, icont)[0]
			except:
				book['cover'] = ''
		if not self.timerule == '':
			try:
				book['time'] = findstr(self.timerule, icont)[0]
			except:
				book['time'] = ''
		if not self.lastrule == '':
			try:
				book['last'] = findstr(self.lastrule, icont)[0]
			except:
				book['last'] = ''
		if not self.desrule == '':
			try:
				book['des'] = findstr(self.desrule, icont)[0]
			except:
				book['des'] = ''
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
		cinfo = weblib().get(book['url'], chardet=True)
		cinfo = cinfo.split(self.listleft)[1].split(self.listright)[0]
		chaps = findstr(self.listrule, cinfo)
		for chap in chaps:
			if not 'http' in chap[0]:
				url = self.baseurl + chap[0]
			else:
				url = chap[0]
			self.chapters.append({'title': chap[1], 'url': url})
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
		content = findstr(self.chaprule, ccont)[0]
		for item in self.chapclean:
			content = content.replace(item, '')
		for item in self.chapcleanre:
			content = re.sub(item, '', content)
		content = re.sub('<br.*?>', '<br />　　', content)
		cinfo['content'] = '　　%s' % content
		fn = '%d.html' % (i+1)
		book = self.sresult[self.selection]
		chapdata = self.output
		chapdata = chapdata.replace('\\n', '\n').replace('{title}', cinfo['title']).replace('{author}', book['author']).replace('{url}', cinfo['url']).replace('{content}', cinfo['content'])
		filelib().write('%s/%s' % (self.path, fn), chapdata, encoding='utf-8')