import sys, os, re
sys.path.append(os.getcwd())
from zutils.file import filelib
from zutils.novel import booklib
from zutils.string import findstr
from zutils.epub import epublib

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
	'makeEpub': '\n创建Epub文件中…',
	'makeEpubComplete': '创建Epub文件完成！'
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
	def getBook(self):
		plugins = PluginManager()
		plugins.showLoaded()
		# select plugin
		plugin = plugins.plugins[int(input(lang['selectPlugin']))-1]
		# search books
		sresult = plugin.search(input(lang['searchKeyword']))
		print(lang['searchResultBelow'])
		for i in range(0, len(sresult)):
			print("\t%d.\t%s%s\n\t\t%s%s" % (i+1, lang['bookName'], sresult[i]['title'], lang['bookAuthor'], sresult[i]['author']))
		# display selected book info
		self.binfo = plugin.getInfo(int(input(lang['selectBook']))-1)
		print("%s\n\t%s\t%s\n\t%s\t%s\n\t%s\t%s\n\t%s%s\n\t%s%s" % (lang['bookInfo'], lang['bookName'], self.binfo['title'], lang['bookAuthor'], self.binfo['author'], lang['bookIntro'], self.binfo['des'], lang['lastUpdated'], self.binfo['time'], lang['lastChapter'], self.binfo['last']))
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
		# Then download the book into seperate html file.
		# and create a cata html file.
		print(lang['downloading'])
		self.path = plugin.download(self.count)
		print(lang['downloadComplete'])
	def makeBook(self):
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

if __name__ == '__main__':
	novel = NovelPush()
	novel.getBook()
	novel.makeBook()