import requests
from urllib.request import urlretrieve

class weblib:
	def __init__(self):
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
		}
		self.jar = requests.cookies.RequestsCookieJar()
	def setCookie(self, key, value):
		self.jar.set(key, value)
	def getCookie(self):
		return requests.utils.dict_from_cookiejar(self.cookies)
	def get(self, url, chardet=False):
		try:
			req = requests.get(url, headers = self.headers, cookies = self.jar, timeout=90)
			self.cookies = req.cookies
			if chardet:
				req.encoding = requests.utils.get_encodings_from_content(req.text)[0]
			return req.text
		except:
			return ''
	def post(self, url, postdata, chardet=False):
		try:
			req = requests.post(url, headers = self.headers, cookies = self.jar, data = postdata, timeout=90)
			self.cookies = req.cookies
			if chardet:
				req.encoding = requests.utils.get_encodings_from_content(req.text)[0]
			return req.text
		except:
			return ''
	def download(self, url, filename):
		urlretrieve(url, filename)