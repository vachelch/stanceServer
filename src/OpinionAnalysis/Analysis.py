#coding=utf-8
import os
import logging
import jieba
import time
import json

from pathos.pools import ProcessPool
import pandas as pd
import numpy as np

import OpinionAnalysis.bert.run_classifier as bert

def get_news_opinion(json_data, num_cores, text, w2v, global_set):
	df_data = tag_and_write_for_CopeOpi(json_data, num_cores, text, w2v, global_set)
	return df_data

def tag_and_write_for_CopeOpi(json_data, num_cores, text, w2v, global_set, method='CKIP'):
	def param_generator(json_data):
		for data in json_data:
			yield data['id'], data['title'], data['content']

	def param_generator_seq(json_data):
		resultList = list()
		for data in json_data:
			resultList.append([data['id'], data['title'], data['content']])
		return resultList

	def tag_and_write_job(dataList):
		dataList = np.array(dataList)
		ids = dataList[:, 0]
		stance_pair = [dataList[:, 1:]]

		stance_pair = []
		for ariticle in dataList[:, 1:]:
			news_title, news_content = ariticle
			bodyText = "{} {}".format(news_title, news_content)
			stance_pair.append([text, bodyText])	

		stances = bert.predict(stance_pair, global_set)

		# new_json_data = [{}, ]
		new_json_data = list()
		for num_x, _stance in zip(ids, stances):
			new_json_data.append({'id':int(num_x),'stance': _stance})
		
		return new_json_data


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

	new_json_data = tag_and_write_job(dataList)

	print("predict time: {} s".format(time.time()-startTime))

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



