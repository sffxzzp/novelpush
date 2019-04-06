import os, json, re, shutil

class filelib:
	def open(self, path, mode='r', encoding="gbk"):
		try:
			with open(path, mode, encoding=encoding) as f:
				content = f.read()
			return content
		except:
			return False
	def write(self, path, content, mode='w', encoding="gbk"):
		with open(path, mode, encoding=encoding) as f:
			f.write(content)
		return True
	def copy(self, source, target):
		try:
			shutil.copy(source, target)
		except:
			pass
	def json(self, path):
		cont = self.open(path, encoding="utf-8")
		if cont:
			cont = re.sub('(?<!:)\\/\\/.*|\\/\\*(\\s|.)*?\\*\\/', '', cont)
			cont = cont.replace('\\', '\\\\').replace('\\\\"', '\\"')
			return json.loads(cont)
		else:
			return False
	def exists(self, path):
		return os.path.exists(path)
	def mkdir(self, path):
		path = path.strip().rstrip('\\')
		if not os.path.exists(path):
			os.makedirs(path)