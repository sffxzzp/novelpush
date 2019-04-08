import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

class maillib:
	def init(self, info):
		self.info = info
	def subject(self, subject):
		self.message = MIMEMultipart()
		self.message['From'] = 'NovelPush <%s>' % self.info['FromEmail']
		self.message['To'] = self.info['ToEmail']
		self.message['Subject'] = Header(subject, 'utf-8')
	def main(self, text):
		self.message.attach(MIMEText(text, 'plain', 'utf-8'))
	def attach(self, name, path):
		att = MIMEApplication(open(path, 'rb').read())
		att.add_header('Content-Disposition', 'attachment', filename=name)
		self.message.attach(att)
	def send(self):
		try:
			if self.info['Port'] > 100:
				server = smtplib.SMTP_SSL(self.info['Server'], self.info['Port'])
			else:
				server = smtplib.SMTP(self.info['Server'], self.info['Port'])
			server.login(self.info['Username'], self.info['Password'])
			server.sendmail(self.info['FromEmail'], [self.info['ToEmail'],], self.message.as_string())
			server.quit()
		except smtplib.SMTPException as e:
			print('Error: ', e)