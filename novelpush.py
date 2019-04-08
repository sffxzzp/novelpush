import sys, os, re, json
sys.path.append(os.getcwd())
from zutils.file import filelib
from zutils.novel import booklib
from zutils.string import findstr
from zutils.epub import epublib
from zutils.email import maillib

lang = {
	'pluginLoaded': '从插件中加载的站点如下：',
	'selectPlugin': '\n请输入要使用的站点编号：',
	'searchKeyword': '请输入要搜索的关键词：',
	'searchResultBelow': '\n搜索结果如下：',
	'waitDownload': '\n已下载 %s 章，共 %s 章。\n请按回车键开始下载…',
	'bookName': '书名：',
	'bookAuthor': '作者：',
	'selectBook': '请输入要下载的书籍编号：',
	'bookInfo': '\n选择的书籍详细信息如下：',
	'bookIntro': '简介：',
	'lastUpdated': '更新时间：',
	'lastChapter': '最新章节：',
	'downloading': '\n正在下载：',
	'downloadComplete': '下载完成！',
	'makeEpub': '\n创建 Epub 文件中…',
	'makeEpubComplete': '创建 Epub 文件完成！',
	'epubAlreadyExists': 'Epub 文件已存在',
	'initConfig': '检测到配置信息不全。\n请遵循提示，填写信息。\n',
	'configSaved': '\n配置保存完毕！\n',
	'SMTPServer': 'SMTP 服务器：',
	'SMTPUsername': 'SMTP 用户名：',
	'SMTPPassword': 'SMTP 密码：',
	'SMTPFrom': '发件箱：',
	'SMTPTo': '收件箱：',
	'sendEmail': '\n正在发送书籍至：%s',
	'emailSent': '邮件已发送！'
}

class PluginManager:
	def __init__(self):
		self.plugins = []
		self.loadPlugins()
	def loadPlugins(self):
		for filename in os.listdir("plugins"):
			name = os.path.splitext(filename)[0]
			if filename.endswith("py"):
				self.runPluginPython(name)
			if filename.endswith("json"):
				self.runPluginJSON(name)
	def runPluginPython(self, name):
		plugin = __import__("plugins."+name, fromlist=[name])
		pclass = plugin.getClass(self)
		if pclass.enabled:
			self.plugins.append(pclass)
	def runPluginJSON(self, name):
		book = booklib(name)
		if book.enabled:
			self.plugins.append(book)
	def showLoaded(self):
		print(lang['pluginLoaded'])
		for i in range(0, len(self.plugins)):
			print("\t%d. %s" % (i+1, self.plugins[i].url))

class NovelPush:
	def __init__(self):
		self.cssfile = 'books/stylesheet.css'
		self.coverfile = 'books/titlepage.html'
		self.settings = 'settings.json'
		self.lastPlugin = 0
		self.lastSearch = ''
		self.lastSelect = 0
		self.smtp = {}
	def getConfig(self):
		cfgfile = filelib().json(self.settings)
		if not cfgfile:
			self.initConfig()
		else:
			if 'Last' in cfgfile:
				if 'Plugin' in cfgfile['Last']:
					self.lastPlugin = cfgfile['Last']['Plugin']
				if 'Search' in cfgfile['Last']:
					self.lastSearch = cfgfile['Last']['Search']
				if 'Select' in cfgfile['Last']:
					self.lastSelect = cfgfile['Last']['Select']
			if 'SMTP' in cfgfile:
				valid = True
				for name in ['Server', 'SSL', 'Port', 'Username', 'Password', 'FromEmail', 'ToEmail']:
					if name not in cfgfile['SMTP']:
						valid = False
				if valid:
					self.smtp = cfgfile['SMTP']
				else:
					self.initConfig()
			else:
				self.initConfig()
	def initConfig(self):
		print(lang['initConfig'])
		cfgfile = {
			"Last": {
				"Plugin": 0,
				"Search": "",
				"Select": 0
			},
			"SMTP": {
				"Server": input(lang['SMTPServer']),
				"SSL": True,
				"Port": 465,
				"Username": input(lang['SMTPUsername']),
				"Password": input(lang['SMTPPassword']),
				"FromEmail": input(lang['SMTPFrom']),
				"ToEmail": input(lang['SMTPTo'])
			}
		}
		self.writeConfig(cfgfile)
		print(lang['configSaved'])
	def saveConfig(self):
		cfgfile = {
			"Last": {
				"Plugin": self.lastPlugin,
				"Search": self.lastSearch,
				"Select": self.lastSelect
			},
			"SMTP": self.smtp
		}
		self.writeConfig(cfgfile)
	def clearConfig(self):
		cfgfile = {
			"Last": {
				"Plugin": 0,
				"Search": "",
				"Select": 0
			},
			"SMTP": self.smtp
		}
		self.writeConfig(cfgfile)
	def writeConfig(self, cfgfile):
		filelib().write(self.settings, json.dumps(cfgfile, ensure_ascii=False), encoding='utf-8')
	def getBook(self):
		self.getConfig()
		plugins = PluginManager()
		plugins.showLoaded()
		# select plugin
		if self.lastPlugin == 0:
			self.lastPlugin = int(input(lang['selectPlugin']))
		plugin = plugins.plugins[self.lastPlugin-1]
		# search books
		if self.lastSearch == '':
			self.lastSearch = input(lang['searchKeyword'])
		print(self.lastSearch)
		sresult = plugin.search(self.lastSearch)
		print(lang['searchResultBelow'])
		for i in range(0, len(sresult)):
			print("\t%d.\t%s%s\n\t\t%s%s" % (i+1, lang['bookName'], sresult[i]['title'], lang['bookAuthor'], sresult[i]['author']))
		# display selected book info
		if self.lastSelect == 0:
			self.lastSelect = int(input(lang['selectBook']))
		self.binfo = plugin.getInfo(self.lastSelect-1)
		print("%s\n\t%s\t%s\n\t%s\t%s\n\t%s\t%s\n\t%s%s\n\t%s%s" % (lang['bookInfo'], lang['bookName'], self.binfo['title'], lang['bookAuthor'], self.binfo['author'], lang['bookIntro'], self.binfo['des'], lang['lastUpdated'], self.binfo['time'], lang['lastChapter'], self.binfo['last']))
		self.saveConfig()
		# check difference under `books` folder
		# books folder should structured like below
		# books
		# |- pluginName1
		#    |- bookID
		#       |- 1.html
		#       |- 2.html
		#       |- ...
		#       |- n.html
		# |- pluginName2
		# different plugin has different folder, which could ensure downloaded files are exactly the same.
		# and all that left is only count the number of the files, which means the progress in catalog, and that is the start of download this time.
		# and read the last file in folder to print title of the last chapter.
		self.count = plugin.checkStart()
		self.chapters = plugin.getCata()
		input(lang['waitDownload'] % (self.count, len(self.chapters)))
		self.clearConfig()
		# Then download the book into seperate html file.
		# and create a cata html file.
		print(lang['downloading'])
		self.path = plugin.download(self.count)
		print(lang['downloadComplete'])
		# Download complete, and recheck downloaded file num
		# This could fix the newest downloaded files not added to toc and opf file.
		self.count = plugin.checkStart()
	def makeBook(self):
		# check epubpath if book already created.
		self.epubpath = '%s/%s.epub' % ('output', self.binfo['title'])
		if not filelib().exists(self.epubpath):
			print(lang['makeEpub'])
			# copy needed files to target folder.
			filelib().copy(self.cssfile, self.path)
			filelib().copy(self.coverfile, self.path)
			# create epub file.
			book = epublib(self.path)
			book.setMeta({
				'title': self.binfo['title'],
				'author': self.binfo['author'],
				'des': self.binfo['des']
			})
			for i in range(0, self.count):
				book.addChap(i+1, self.chapters[i]['title'])
			book.makeEpub()
			print(lang['makeEpubComplete'])
		else:
			print(lang['epubAlreadyExists'])
	def sendMail(self):
		print(lang['sendEmail'] % self.smtp['ToEmail'])
		email = maillib()
		email.init(self.smtp)
		email.subject(self.binfo['title'])
		email.main('书名：%s\n作者：%s' % (self.binfo['title'], self.binfo['author']))
		email.attach('%s.epub' % self.binfo['title'], self.epubpath)
		email.send()
		print(lang['emailSent'])

if __name__ == '__main__':
	novel = NovelPush()
	novel.getBook()
	novel.makeBook()
	novel.sendMail()