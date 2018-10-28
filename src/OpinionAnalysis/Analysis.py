#coding=utf-8
import os
import logging
import jieba
# from nltk.tag import StanfordPOSTagger
import time

from pathos.pools import ProcessPool
import pandas as pd
import json

try:
	from OpinionAnalysis.GetOpinion import CopeOpiAnalyzer
	from OpinionAnalysis.ckipsvr import CKIPsegmenter
	# from .oneClickStanceClassification import stanceAnalyzer
	from OpinionAnalysis.oneClickStanceClassification import stanceAnalyzerCos
	# from .oneClickStanceClassificationWithNeg import stanceAnalyzerCos
except:
	from OpinionAnalysis.GetOpinion import CopeOpiAnalyzer
	from OpinionAnalysis.ckipsvr import CKIPsegmenter
	# from oneClickStanceClassification import stanceAnalyzer
	from OpinionAnalysis.oneClickStanceClassification import stanceAnalyzerCos
	# from oneClickStanceClassificationWithNeg import stanceAnalyzerCos

def get_news_opinion(json_data, num_cores, text, w2v):
	df_data = tag_and_write_for_CopeOpi(json_data, num_cores, text, w2v)
	return df_data

def tag_and_write_for_CopeOpi(json_data, num_cores, text, w2v, method='CKIP'):
	## JIEBA + Stanford ##
	# print("Init JIEBA")
	# if method == 'JIEBA':
	# 	JIEBAInit('OpinionAnalysis/dict/')
		# SFtagger = StanfordPOSTagger(
		# 'OpinionAnalysis/StanfordPosTagger/models/chinese-distsim.tagger',
		# 'OpinionAnalysis/StanfordPosTagger/stanford-postagger-3.7.0.jar')
	
	# COanalyzer = CopeOpiAnalyzer('OpinionAnalysis/dict/')
	# if not os.path.exists('./OpinionAnalysis/data'):
	# 	os.makedirs('./OpinionAnalysis/data')
	# if not os.path.exists('./OpinionAnalysis/log'):
	# 	os.makedirs('./OpinionAnalysis/log')

	def param_generator(json_data):
		for data in json_data:
			yield data['id'], data['title'], data['content']

	def param_generator_seq(json_data):
		resultList = list()
		for data in json_data:
			resultList.append([data['id'], data['title'], data['content']])
		return resultList

	def tag_and_write_job(param):
		num_x, news_title, news_content = param

		logging.info("Processing news #{}".format(num_x))

		## JIEBA + Stanford ##
		'''
		seg_output = list(jieba.cut(news_content.replace('\xa0',' ')))
		stanford_output = SFtagger.tag(seg_output)
		news_content = ''

		for out in stanford_output:
			news_content += out[1].split('#')[0] + '(' + Stanford2CKIP(out[1].split('#')[1]) + ') '
		'''
		# prefix = "反對"
		bodyText = "{} {}".format(news_title, news_content)
		# _stance = stanceAnalyzer(prefix+text, bodyText, w2v)
		_stance = stanceAnalyzerCos(text, bodyText, w2v)
		if _stance == "discuss":
			_stance = "neutral"
		# print("{} vs {} : {}".format(text, bodyText, _stance))
		print("[RESULT] News #{} stance : {} ".format(num_x, _stance))

		## CKIP ##
		# news_content = ' '.join(CKIPsegmenter(news_content))
		# news_title = ' '.join(CKIPsegmenter(clean_title(news_title)))

		# totalScore, outString = COanalyzer.score(news_content)
		# titleScore, _ = COanalyzer.score(news_title)

		# # save processed text
		# filepath = 'OpinionAnalysis/data/{}.txt'.format(num_x)
		# with open(filepath, 'w') as fp:
		# 	fp.write(news_content)

		# # save CopeOpi output
		# filepath = 'OpinionAnalysis/log/{}.txt'.format(num_x)
		# with open(filepath, 'w') as fp:
		# 	fp.write(outString)
	
		# totalOpi = Score2Opi(totalScore, 0.1, -0.1)
		# titleOpi = Score2Opi(titleScore, 0.2, -0.2)
		# return {'id':num_x, 'score':totalScore, 'opi':totalOpi,
		# 		't_score': titleScore, 't_opi':titleOpi,
		# 		'stance': _stance}
		return {'id':num_x,'stance': _stance}


	pool = ProcessPool(num_cores)
	json_dataFiltered = list()
	for data in json_data:
		#filter out the unrelated NEWS
		if "歷史上的今天" in data['title']:
			continue
		json_dataFiltered.append(data)
	json_data = json_dataFiltered
	# print("get map functions")
	startTime = time.time()
	# new_json_data = pool.map(tag_and_write_job, param_generator(json_data))
	new_json_data = list()
	dataList = param_generator_seq(json_data)
	for ele in dataList:
		new_json_data.append(tag_and_write_job(ele))
	print("Cost time : {}secs".format(time.time()-startTime))

	df = pd.DataFrame(json_data)
	df_new = pd.DataFrame(new_json_data)
	ret_df = df.merge(df_new, left_on='id', right_on='id')
	ret_json = json.loads(ret_df.to_json(orient='records'))

	return ret_json

def JIEBAInit(file_path='OpinionAnalysis/dict/'):
	logging.info('Loading dictionary and initializing jieba...')
	jieba.set_dictionary(file_path+'dict.txt.big')
	jieba.load_userdict(file_path+'userdict.txt')
	jieba.initialize()

def Score2Opi(score, pos_thread, neg_thread):
	if score > pos_thread:
		return 'Positive'
	elif score < neg_thread:
		return 'Negative'
	else:
		return 'Neutral'

def clean_title(input_string):
	'''
	delete some unmeaning words in title
	'''
	input_string = input_string.replace('聯合筆記／','').replace('聯合／','').replace('自由廣場》','').replace('《新聞分析》','')
	return input_string

def Stanford2CKIP(x):
	try:
		return {
	        'AD':'D',
			'NT':'Nd',
			'NT-SHORT':'Nd',
			'OD':'Neu',
			'VA':'VA',
			'NN':'Nb',
			'VV':'VG',
			'NR':'Nb',
			'DT':'Ne',
			'PN':'Nh',
			'JJ':'Na',
			'CS':'Cba',
			'LC':'Ncd',
			'M':'Nf',
			'CC':'C',
			'AS':'T',
			'VC':'SHI',
			'P':'P',
			'DEC':'DE',
			'DEG':'DE',
			'DER':'DE',
			'NR-SHORT':'Nb',
			'SP':'T',
			'VE':'V_2',
			'NN-SHORT':'Na',
			'MSP':'D',
			'NP':'Na',
			'LB':'P',
			'SB':'P',
			'IJ':'I',
			'ETC':'Cab',
			'DEV':'DE',
			'BA':'P',
			'PU':'PERIODCATEGORY',
			'CD':'CD'
		}[x]
	except KeyError: # if x does not exist in this mapping, return x
		logging.info('key "{}" does not exist in Stanford2CKIP mapping.'.format(x))
		return(x)

