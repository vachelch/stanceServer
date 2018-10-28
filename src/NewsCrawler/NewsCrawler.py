#coding=utf-8

'''
functions to retrieve the content of an individual link
'''
import requests
import urllib
import logging
from bs4 import BeautifulSoup

from pathos.pools import ProcessPool
import pandas as pd
import json

def get_full_content(json_data, num_cores):

	def param_generator(json_data):
		for data in json_data:
			yield data['id'], data['url']

	def tag_and_write_job(param):
		num_x, news_url = param
		logging.info("Processing news #{}: {}".format(num_x, news_url))

		news_content = GetUrlContent(news_url)

		## store all news (might be used for word2vec) ##
		with open('OpinionAnalysis/data/news_corpus.txt', 'a') as fp:
			fp.write('*\n')
			fp.write(news_content)

		return {'id':num_x, 'content':news_content}

	pool = ProcessPool(num_cores)
	new_json_data = pool.map(tag_and_write_job, param_generator(json_data))

	df = pd.DataFrame(json_data)
	df_new = pd.DataFrame(new_json_data)
	ret_df = df.merge(df_new, left_on='id', right_on='id')
	ret_json = json.loads(ret_df.to_json(orient='records'))

	return ret_json

def GetUrlContent(news_url):
	'''
	Retrieve contents of an url
	'''
	try:
		res = requests.get(news_url)
		if res.encoding == 'ISO-8859-1':
			res.encoding = 'utf-8'
		soup = BeautifulSoup(res.text, "lxml")
	except:
		logging.warning('requests blocked by the website ({})'.format(news_url))
		return('')

	if 'news.tvbs.com.tw/' in news_url:
		div_tag = soup.find_all('div', class_='newsdetail-content')
		content = TVBSNewsContent(div_tag)
	
	elif 'www.bbc.com/' in news_url or 'www.ettoday.net' in news_url or 'sports.ettoday.net' in news_url:
		div_tag = soup.find_all('div', class_='story')
		content = collect_content(div_tag)

	elif 'udn.com/news' in news_url:
		div_tag = soup.find_all('div', id='story_body')
		content = collect_content(div_tag)

	elif 'www.cw.com.tw' in news_url or 'www.peoplenews.tw' in news_url:
		div_tag = soup.find_all('div', class_='main')
		content = collect_content(div_tag)

	elif 'newtalk.tw/news' in news_url:
		div_tag = soup.find_all('div', id='news_content')
		content = collect_content(div_tag)

	elif 'www.setn.com' in news_url:
		div_tag = soup.find_all('div', id='Content1')
		content = collect_content(div_tag)

	elif 'news.ltn.com.tw' in news_url:
		div_tag = soup.find_all('div', class_='text') 
		content = collect_content(div_tag)

	elif 'talk.ltn.com.tw' in news_url:
		div_tag = soup.find_all('div', class_='cont') 
		content = collect_content(div_tag)

	elif 'ent.ltn.com.tw/' in news_url:
		div_tag = soup.find_all('div', id='ob') 
		content = collect_content(div_tag)

	elif 'www.appledaily.com.tw' in news_url:
		div_tag = soup.find_all('article', id='maincontent') 
		content = collect_content(div_tag)

		delete_index = content.find('【小編推薦，大家都在看')
		if delete_index > 0:
			content = content[0:delete_index]

	else:
		# heuristics
		# delete: div, id = articleContentBody, ArticleText
		# delete: id='articleText'
		div0 = soup.find_all('article') # www.nownews.com
		div1 = soup.find_all('div', id='news_content') # 
		div2 = soup.find_all('div', id='article_content')
		div3 = soup.find_all('div', id='story_body') # nba.udn.com
		div4 = soup.find_all('div', id='newstext')
		div5 = soup.find_all('div', id='container') # opinion.udn.com

		div6 = soup.find_all('div', class_='news_content') 
		div7 = soup.find_all('div', class_='news_text') 
		div8 = soup.find_all('div', class_='ArticleText')
		div9 = soup.find_all('div', class_='articleBodyText')

		div10 = soup.find_all('div', class_='content') 
		div11 = soup.find_all('div', class_='story')
		div12 = soup.find_all('div', class_='story-container')
		div13 = soup.find_all('div', class_='main-text') # www.peoplenews.tw, 
		div14 = soup.find_all('div', class_='main')
		div15 = soup.find_all('div', class_='body')
		div16 = soup.find_all('div', class_='article__body')
		div17 = soup.find_all('div', class_='article-content') # www.thenewslens.com 
	
		if div0:
			logging.info('Getting Link Content: div0')
			content = collect_content(div0)
		elif div1:
			logging.info('Getting Link Content: div1')
			content = collect_content(div1)
		elif div2:
			logging.info('Getting Link Content: div2')
			content = collect_content(div2)
		elif div3:
			logging.info('Getting Link Content: div3')
			content = collect_content(div3)
		elif div4: 
			logging.info('Getting Link Content: div4')
			content = collect_content(div4)
		elif div5: 
			logging.info('Getting Link Content: div5')
			content = collect_content(div5)
		elif div6: 
			logging.info('Getting Link Content: div6')
			content = collect_content(div6)
		elif div7:
			logging.info('Getting Link Content: div7')
			content = collect_content(div7)
		elif div8:
			logging.info('Getting Link Content: div8')
			content = collect_content(div8)
		elif div9:
			logging.info('Getting Link Content: div9')
			content = collect_content(div9)
		elif div10:
			logging.info('Getting Link Content: div10')
			content = collect_content(div10)
		elif div11: 
			logging.info('Getting Link Content: div11')
			content = collect_content(div11)
		elif div12:
			logging.info('Getting Link Content: div12')
			content = collect_content(div12)
		elif div13: 
			logging.info('Getting Link Content: div13')
			content = collect_content(div13)
		elif div14: 
			logging.info('Getting Link Content: div14')
			content = collect_content(div14)
		elif div15: 
			logging.info('Getting Link Content: div15')
			content = collect_content(div15)
		elif div16: 
			logging.info('Getting Link Content: div16')
			content = collect_content(div16)
		elif div17: 
			logging.info('Getting Link Content: div17')
			content = collect_content(div17)
		else: # www.appledaily.com.tw, www.thenewslens.com http://www.chinatimes.com/
			logging.info('Getting Link Content: none')
			c_list = [v.text for v in soup.find_all('p') if len(v.text) > 0]
			words_to_bans = ['<', 'javascript', 'function('] # can add new words to ban here
			for word_to_ban in words_to_bans:
				c_list = list(filter(lambda x: word_to_ban not in x.lower(), c_list))
			content = '\n'.join(c_list)

	content = clean_content(content)
	return(content)

def TVBSNewsContent(div_tag):
	if len(div_tag) == 0:
		return ''
	c_list = [str(v) for v in div_tag[0].contents]
	words_to_bans = ['<', '\n', 'OneAD', ' '] # can add new words to ban here
	for word_to_ban in words_to_bans:
		c_list = list(filter(lambda x: word_to_ban not in x.lower(), c_list))
	content = '\n'.join(c_list)
	return(content)

def collect_content(parent_tag, element_to_ban=['script', 'span']):
	'''
	Collects all text from all <p> of parent_tag
	'''
	content = ''
	for child_tags in parent_tag:
		gradchild_tag = child_tags.find_all('p')
		for tag in gradchild_tag:
			if tag.next_element.name not in element_to_ban:
				content += tag.text + '\n'
	return content

def clean_content(content):
	content = content.replace('\r', '\n').replace('\n', '。').replace('。。', '。')
	# 中央社新聞冗言
	content = content.replace('（中央社）', '').replace('延伸閱讀：','').replace('綜合報導', '').replace('即時新聞', '')
	content = content.replace('發稿時間：', '').replace('最新更新：','')
	content = content.replace('〔／〕', '').replace('[]', '')
	# 公視新聞
	content = content.replace('文/', '').replace('名稱(必填)', '').replace('email(必填；網站不會顯示此資訊)', '') 
	# 自由時報電子報
	content = content.replace('／特稿', '').replace('（資料照）', '')
	# content = content.replace('快加入APP、LINE好友', '').replace('LINE好友。', '').replace('快加入自由電子報APP、LINE好友', '')
	# content = content.replace('手機版|電腦版', '').replace('熱門推播。', '')
	# 東森新聞
	content = content.replace('政治中心／', '').replace('▲', '').replace('◎', '')
	# 蘋果日報
	content = content.replace('版權所有不得轉載', '').replace('版權所有 不得轉載', '')
	# 天下
	content = content.replace('圖片來源：', '').replace('訂閱全閱讀，全站通行', '').replace('造訪我的網站', '')
	# 聯合
	content = content.replace('圖／截自', '圖截自').replace('聯合報系資料照', '').replace('分享   facebook', '')
	content = content.replace('更多精采內容，詳見', '')
	# 中時
	content = content.replace('(中時電子報)', '')
	# thenewslens
	content = content.replace('核稿編輯：', '') 

	return(content)
