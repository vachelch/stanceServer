import socket
import xml.parsers.expat
from time import sleep
import logging

my_format = "<?xml version=\"1.0\"?><wordsegmentation version=\"0.1\" charsetcode=\"utf-8\"><option showcategory=\"1\"/>%s<text>%s</text></wordsegmentation>"
authentication_string = "<authentication username=\"vinceliu\" password=\"vincent13\"/>"
connect_target = ("140.109.19.104", 1501)

class parse_xml:
	def __init__(self, input_xml_str):
		self.status_code, self.status_str, self.result = None, '', ''
		self.core = xml.parsers.expat.ParserCreate('utf-8')
		self.core.StartElementHandler = self.start_element
		self.core.EndElementHandler = self.end_element
		self.core.CharacterDataHandler = self.char_data
		self.pointer = None
		if type(input_xml_str) is str:
			self.core.Parse(input_xml_str.strip(),1)
		else:
			self.core.Parse(input_xml_str.encode('utf-8').strip(),1)
	def start_element(self,name,attrs):
		if name == "processstatus":
			self.status_code = int(attrs['code'])
			self.pointer = name
		elif name == "sentence":
			self.pointer = name
	def end_element(self,name):
		if name == "wordsegmentation":
			self.result = self.result.strip()
	def char_data(self,data):
		if self.pointer is None:
			return None
		if self.pointer == "processstatus":
			self.status_str = data
		elif self.pointer == "sentence":
			self.result+= data
		self.pointer = None

def CKIPsegmenter(input_text):
	input_text = input_text.replace('　',' ').strip()
	input_text = input_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
	input_text = input_text.replace('\'','&apos;').replace('"', '&quot;').replace('#', '&sharp;')
	if input_text == '':
		logging.warning('ckipsvr input string is empty')
		return('')
	if len(input_text) >= 7000:
		logging.warning('ckipsvr input string is too long')
		return('')
	
	out_string = send_requests(input_text)

	# if status code 2, try two more times
	if out_string == '':
		sleep(1)
		out_string = send_requests(input_text)
	
	out_string = Ckip2CopeOpi(out_string)
	return out_string.split()

def send_requests(input_text):
	text = my_format % (authentication_string, input_text)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(connect_target)
	try:
		sock.sendall(text)
		downloaded = ''
		stop_word = "</wordsegmentation>"
	except:
		sock.sendall(text.encode('utf-8'))
		downloaded = b''
		stop_word = b"</wordsegmentation>"

	while stop_word not in downloaded:
		chunk = sock.recv(4096)
		downloaded += chunk

	try:
		result = parse_xml(downloaded.decode('utf-8'))
	except:
		logging.warning("ckipsvr decode error")
		return('')

	if result.status_code == 0:
		return(result.result)
	else:
		logging.warning("ckipsvr status code: {}, {}".format(result.status_code, result.status_str))
		return('')

def Ckip2CopeOpi(text):
	text = text.replace('(C)', '(Cbb)').replace('(N)', '(Na)').replace('(ADV)', '(D)').replace('(ASP)', '(Di)').replace('(DET)', '(Neu)')
	return text

def delete_tag(text): 
	'''
	delete all tags
	'''
	text = text.replace('(A)', '').replace('(C)', '').replace('(POST)', '')
	text = text.replace('ADV', '').replace('(T)', '').replace('(ASP)', '')
	text = text.replace('(FW)', '').replace('(N)', '').replace('(DET)', '')
	text = text.replace('(M)', '').replace('(Nv)', '').replace('(P)', '')
	text = text.replace('(Vt)', '').replace('(Vi)', '').replace('(b)', '')
	text = text.replace('(COMMACATEGORY)', '').replace('(PERIODCATEGORY)', '').replace('(QUESTIONCATEGORY)', '')
	text = text.replace('(PARENTHESISCATEGORY)', '').replace('(PAUSECATEGORY)', '').replace('(SEMICOLONCATEGORY)', '')
	text = text.replace('(DASHCATEGORY)', '').replace('(COLONCATEGORY)', '').replace('()', '')
	return(text)