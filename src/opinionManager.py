#coding=utf-8
from datetime import datetime, timedelta
import pandas as pd
import logging
import time
from urllib.parse import unquote

from NewsCrawler import get_Google_news, get_full_content
from OpinionAnalysis import get_news_opinion
from OpinionDB import OpinionDB

import numpy as np

# from gensim.models import word2vec
from gensim.models import KeyedVectors
def LoadModel(modelFilename, binOrNot=False):
	# model = word2vec.KeyedVectors.load_word2vec_format(modelFilename, binary=binOrNot)
	model = KeyedVectors.load_word2vec_format(modelFilename, binary=binOrNot)
	print("[INFO] Finish loading w2v")
	return model

def printClaim2File(filename, claimText, claimTextRm):
	_file = open(filename, "a")
	_file.write("==========================\n")
	_file.write("Time : {}\n".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
	_file.write("Claim : {}\n".format(claimText))
	_file.write("News Search : {}\n".format(claimTextRm))
	_file.close()

class OpinionManager(object):
	def __init__(self, db_path, w2v_path, global_set):
		self.db= OpinionDB(db_path)
		self.w2v = LoadModel(w2v_path, True)
		self.global_set = global_set

	def get_two_side_news(self, text, count):
		original_news_data = get_Google_news(text, count)
		opposite_news_data = get_Google_news('反'+text, count)
		# delete duplicate urls
		for n2 in opposite_news_data[:]:
			for n1 in original_news_data:
				if n2['url'] == n1['url']:
					opposite_news_data.remove(n2)
					continue
		original_news_data.extend(opposite_news_data)
		# reset id 
		for x in range(len(original_news_data)):
			original_news_data[x]['id'] = x
		return original_news_data

	def retrieve(self, text, count, core_crawler=12, core_analyzer=12):
		"""
		    1. Get news urls
		    2. Compare with db
		    3. Analyse and insert those aren't in db
		    4. Return results
		"""

		# Get google news list (url, title,...). will use bing news search API later
		# if text in ['一例一休', '年金改革', '年改']:
		# 	news_data = self.get_two_side_news(text, count)
		# else:
		# tmp solution rm 支持 or 反對 in claim
		removeStanceWordList = ["不支持", "支持", "不反對", "反對", "不同意", "同意"]
		searchText = text
		for stanceW in removeStanceWordList:
			if stanceW in searchText:
				searchText = searchText.replace(stanceW, "")
				# break
		print("[CLAIM] Search Claim : {}".format(searchText))
		printClaim2File("./ClaimLog.log", text, searchText)
		news_data = get_Google_news(searchText, count)

		# Filter new urls with DB
		# parse url
		for i in range(len(news_data)):
			news_data[i]['url'] = unquote(news_data[i]['url'])

		urls = [ d['url'] for d in news_data ]
		exist_urls, not_exist_urls = self.db.filter(urls)
		logging.info('News in db: {}. News not in db: {}'.format(len(exist_urls), len(not_exist_urls)))

		data = []
		if len(not_exist_urls) != 0:
			# if len(not_exist_urls):
			filtered_news_data = [ d for d in news_data if d['url'] in not_exist_urls ]

			# Get news content for these news
			filtered_news_content = get_full_content(filtered_news_data, core_crawler)

			# Get Not Exist Opinion Scores
			print("Get Stance")
			json_data = get_news_opinion(filtered_news_content, core_analyzer, text, self.w2v, self.global_set)

			# Reformat to list for db insertion
			for row_dict in json_data:
				# row = ( row_dict['url'],
				# 		row_dict['title'],
				# 		row_dict['opi'],
				# 		row_dict['score'],
				# 		row_dict['t_opi'],
				# 		row_dict['t_score'],
				# 		row_dict['website'],
				# 		row_dict['date'],
				# 		row_dict['stance'])
				row = [ "", # query
						row_dict['url'],
						row_dict['title'],
						row_dict['website'],
						row_dict['date'],
						row_dict['stance'],
						None]
				data.append(row)

		# in datebace
		for url in exist_urls:
			row = self.db.select_url(url)
			row = list(row[:-1]) # drop content
			data.append(row)

		# Build row data for DB
		# self.db.insert(data)

		json_data = self.vec_to_json(data)
		# Select from DB
		# for url_idx, url in enumerate(urls):
		# 	row = self.db.select_url(url)
		# 	if row is not None:
		# 		row_obj = { 'id': url_idx,
		# 					'url': row[0],
		# 					'title': row[1],
		# 					'opi': row[2],
		# 					'score': row[3],
		# 					't_opi': row[4],
		# 					't_score': row[5],
		# 					'website': row[6],
		# 					'date': row[7],
		# 					'stance': row[8] }
		# 		json_data[ url_idx ] = row_obj
		# 	else:
		# 		logging.warning('{} is not in db'.format(url))
		return json_data

	def retrieve_from_local(self):
		data = np.array(self.db.show_all())
		
		return self.vec_to_json(data)

	def vec_to_json(self, data):
		json_data = {}

		for url_idx, row in enumerate(data):
			row_obj = { 'id': url_idx,
						'query': row[0],
						'url': unquote(row[1]),
						'title': row[2],
						'website': row[3],
						'date': row[4],
						'stance': row[5],
						'label': row[6]}

			json_data[ url_idx ] = row_obj

		return json_data
        
	@staticmethod
	def convert_to_chart_data(json_data):
		df = pd.DataFrame(json_data).T
		df['date'] = [datetime.strptime(x, '%Y-%m-%d') for x in df['date']]

		# sentiment
		# summ_df = pd.DataFrame(df.groupby(['date','opi']).size(), columns = ['news_count'])
		# summ_df.reset_index('opi', inplace = True)
		# summ_df.sort_index(inplace = True)

		start_date = min(df['date']) - timedelta(1)
		end_date = max(df['date'])
		num_day = int( (end_date - start_date).days + 1 )
		dates_list = [start_date + timedelta(n) for n in range(num_day)]

		# pos_df = summ_df[summ_df['opi'] == 'Positive']['news_count']
		# neg_df = summ_df[summ_df['opi'] == 'Negative']['news_count']
		# neu_df = summ_df[summ_df['opi'] == 'Neutral']['news_count']

		# pos_count = sum(pos_df.tolist())
		# neg_count = sum(neg_df.tolist())
		# neu_count = sum(neu_df.tolist())

		# pos_df = pos_df.reindex(dates_list, fill_value=0)
		# neg_df = neg_df.reindex(dates_list, fill_value=0)
		# neu_df = neu_df.reindex(dates_list, fill_value=0)

		# dates_list = [x.strftime('%Y-%m-%d') for x in dates_list]

		# pie_chart_data_sentiment = {
		# 	'pos': pos_count,
		# 	'neg': neg_count,
		# 	'neu': neu_count
		# }

		# line_chart_data_sentiment = {
		# 	'date': dates_list,
		# 	'pos': pos_df.tolist(),
		# 	'neg': neg_df.tolist(),
		# 	'neu': neu_df.tolist()
		# }

		# stance
		summ_df = pd.DataFrame(df.groupby(['date','stance']).size(), columns = ['news_count'])
		summ_df.reset_index('stance', inplace = True)
		summ_df.sort_index(inplace = True)

		dates_list_stance = [start_date + timedelta(n) for n in range(num_day)]

		agree_df = summ_df[summ_df['stance'] == 'agree']['news_count']
		disa_df = summ_df[summ_df['stance'] == 'disagree']['news_count']
		# disc_df = summ_df[summ_df['stance'] == 'discuss']['news_count']
		disc_df = summ_df[summ_df['stance'] == 'neutral']['news_count']

		agree_count = sum(agree_df.tolist())
		disa_count = sum(disa_df.tolist())
		disc_count = sum(disc_df.tolist())

		agree_df = agree_df.reindex(dates_list_stance, fill_value=0)
		disa_df = disa_df.reindex(dates_list_stance, fill_value=0)
		disc_df = disc_df.reindex(dates_list_stance, fill_value=0)

		dates_list_stance = [x.strftime('%Y-%m-%d') for x in dates_list_stance]

		pie_chart_data_stance = {
			'pos': agree_count,
			'neg': disa_count,
			'neu': disc_count
		}

		line_chart_data_stance = {
			'date': dates_list_stance,
			'pos': agree_df.tolist(),
			'neg': disa_df.tolist(),
			'neu': disc_df.tolist()
		}

		# return pie_chart_data_sentiment, line_chart_data_sentiment, pie_chart_data_stance, line_chart_data_stance
		return pie_chart_data_stance, line_chart_data_stance

