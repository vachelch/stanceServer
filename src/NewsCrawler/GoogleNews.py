#coding=utf-8

'''
functions to retrieve google news search results, news urls...
'''
import requests
import urllib
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def get_Google_news(keyword, num_news, tbs=0):
	'''
	tbs = 0 (get news by relevence) / 1 (get news by date)
	'''
	num = min(100, num_news) # max number of news for one query
	count = 0
	json_data = []
	queryQuotation = True
	for start in range(0, num_news, num):
		# https://www.google.com.tw/search?q="美牛輸入台灣"&hl=zh-TW&gl=tw&authuser=0&tbm=nws&start=0&num=1&tbs=sbd:0
		if not queryQuotation:
			url = "https://www.google.com.tw/search?q={}&hl=zh-TW&gl=tw&authuser=0&tbm=nws&start={}&num={}&tbs=sbd:{}".format(keyword, start, num, tbs)
		else:
			url = "https://www.google.com.tw/search?q=\"{}\"&hl=zh-TW&gl=tw&authuser=0&tbm=nws&start={}&num={}&tbs=sbd:{}".format(keyword, start, num, tbs)
		res = requests.get(url)
		soup = BeautifulSoup(res.text, "lxml")
		all_div = soup.findAll('div', {'class': 'g'})
		if len(all_div) > 0 and count <= num_news:
			for div in all_div:
				data = ParseGoogleNews(div, count)
				json_data.append(data)
				count += 1
		else: # no more news in google search
			if not len(json_data) == 0:
				break
			queryQuotation = False
	
	# handle no retrive result error
	if len(json_data) == 0:
		url = "https://www.google.com.tw/search?q={}&hl=zh-TW&gl=tw&authuser=0&tbm=nws&start={}&num={}&tbs=sbd:{}".format(keyword, 0, num, 0)
		res = requests.get(url)
		soup = BeautifulSoup(res.text, "lxml")
		all_div = soup.findAll('div', {'class': 'g'})
		if len(all_div) > 0 and count <= num_news:
			for div in all_div:
				data = ParseGoogleNews(div, count)
				json_data.append(data)
				count += 1
	return json_data

def ParseGoogleNews(div, id_num):
	news_title = div.findAll('h3')[0].text
	#
	news_url = div.findAll('h3')[0].findAll('a', href=True)[0].get('href')
	news_url = news_url[news_url.find('?q=')+3:news_url.find('&sa=')]
	news_url = urllib.parse.unquote(news_url) # decode URL
	#
	news_info = div.findAll('div', {'class': 'slp'})[0].text.split(' - ')
	news_website = GetWebsite(news_info[len(news_info)-2]) # the second last one, in case there are more than 2 values
	news_date = GetDate(news_info[len(news_info)-1]) # the last one
	#
	news_description = div.findAll('div', {'class': 'st'})[0].text
	#
	data = {'id':id_num,
		'title':news_title,
		'url':news_url,
		'website':news_website,
		'date':news_date,
		'short':news_description}
	return data

def GetWebsite(news_website):
	news_website = news_website.replace('(新聞發布)', '').replace('(註冊)', '')
	return news_website

def GetDate(news_date):
	if news_date.find('天前') != -1:
		date = datetime.now() - timedelta(days=int(news_date[0]))
	elif news_date.find('小時') != -1:
		date = datetime.now()
	elif news_date.find('分鐘') != -1:
		date = datetime.now()
	else:
		return(news_date.replace('年', '-').replace('月', '-').replace('日', ''))

	return date.strftime('%Y/%m/%d').replace('/','-')
