import os, zlib
from zutils.file import filelib
from zipfile import ZipFile, ZIP_DEFLATED

class epublib:
	def __init__(self, path):
		self.bookid = path
		self.chapters = []
		self.mimetype = 'application/epub+zip'
		self.metacont = '<?xml version="1.0"?>\n<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n<rootfiles>\n<rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>\n</rootfiles>\n</container>'
		self.opfcont = '<?xml version="1.0"  encoding="UTF-8"?>\n<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="bookid" version="2.0">\n<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">\n%(metadata)s\n<meta name="cover" content="cover-image"/>\n</metadata>\n<manifest>\n<item href="toc.ncx" id="ncx" media-type="application/x-dtbncx+xml"/>\n<item href="cover.jpg" id="cover-image" media-type="image/jpeg"/>\n<item href="stylesheet.css" id="css" media-type="text/css"/>\n<item href="titlepage.html" id="cover" media-type="application/xhtml+xml"/>\n%(manifest)s\n</manifest>\n<spine toc="ncx">\n%(ncx)s\n</spine>\n<guide>\n<reference href="titlepage.html" type="cover"/>\n</guide>\n</package>'
		self.opfdc = '<dc:%(name)s>%(value)s</dc:%(name)s>'
		self.opfitem = '<item id="content%(id)s" href="%(href)s" media-type="application/xhtml+xml"/>'
		self.opfitemref = '<itemref idref="content%(id)s"/>'
		self.metadata = ''
		self.manifest = []
		self.ncx = []
		self.ncxcont = '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">\n<head>\n<meta content="%(bookid)s" name="dtb:uid"/>\n<meta content="1" name="dtb:depth"/>\n<meta content="0" name="dtb:totalPageCount"/>\n<meta content="0" name="dtb:maxPageNumber"/>\n</head>\n<docTitle><text>%(title)s</text></docTitle>\n<docAuthor><text>%(author)s</text></docAuthor>\n<navMap>%(navpoints)s</navMap>\n</ncx>'
		self.navpoint = '<navPoint id="content%(id)s" playOrder="%(id)s">\n<navLabel>\n<text>%(title)s</text>\n</navLabel>\n<content src="%(id)s.html"/>\n</navPoint>'
		self.navpoints = []
		self.makeWorkspace()
	def makeWorkspace(self):
		filelib().mkdir('%s/META-INF' % self.bookid)
		filelib().write('%s/mimetype' % self.bookid, self.mimetype)
		filelib().write('%s/META-INF/container.xml' % self.bookid, self.metacont)
	def setMeta(self, meta):
		self.booktitle = meta['title']
		self.bookauthor = meta['author']
		self.bookdes = meta['des']
		self.metadata = '\n'.join([
			self.opfdc % {'name': 'title', 'value': self.booktitle},
			self.opfdc % {'name': 'creator', 'value': self.bookauthor},
			self.opfdc % {'name': 'description', 'value': self.bookdes}
		])
	def addChap(self, cid, ctitle):
		self.chapters.append({'id': cid, 'title': ctitle})
		self.manifest.append(self.opfitem % {'id': cid, 'href': '%d.html' % cid})
		self.ncx.append(self.opfitemref % {'id': cid})
		self.navpoints.append(self.navpoint % {'id': cid, 'title': ctitle})
	def makeEpub(self):
		self.makeOpf()
		self.makeNcx()
		self.makeZip()
	def makeOpf(self):
		filelib().write('%s/content.opf' % self.bookid, self.opfcont % {'metadata': self.metadata, 'manifest': '\n'.join(self.manifest), 'ncx': '\n'.join(self.ncx)}, encoding='utf-8')
	def makeNcx(self):
		filelib().write('%s/toc.ncx' % self.bookid, self.ncxcont % {'bookid': self.bookid, 'title': self.booktitle, 'author': self.bookauthor, 'navpoints': '\n'.join(self.navpoints)}, encoding='utf-8')
	def makeZip(self):
		with ZipFile('%s/%s.epub' % ('output', self.booktitle), 'w', ZIP_DEFLATED, 9) as epubfile:
			rawPath = os.getcwd()
			os.chdir(self.bookid)
			for root, dirs, files in os.walk('.'):
				for f in files:
					epubfile.write(os.path.join(root, f))
			os.chdir(rawPath)