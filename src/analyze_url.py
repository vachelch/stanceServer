#coding=utf-8
import sys
import logging
from NewsCrawler import GetUrlContent
from OpinionAnalysis import CopeOpiAnalyzer
from OpinionAnalysis import CKIPsegmenter 

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
COanalyzer = CopeOpiAnalyzer('OpinionAnalysis/dict/')
if len(sys.argv) == 3:
	if str(sys.argv[1]) == '-u':
		news_content = GetUrlContent(str(sys.argv[2]))
		print('----------------')
		print(news_content)
	elif str(sys.argv[1]) == '-s':
		news_content = str(sys.argv[2])

	docString = ' '.join(CKIPsegmenter(news_content))
	print('----------------')
	print(docString)
	print('----------------')
	totalScore, outString = COanalyzer.score(docString)
	print(outString)

elif len(sys.argv) == 2:
	if str(sys.argv[1]) == '-e':
		import pandas as pd
		file_path = 'OpinionAnalysis/evaluation.csv'
		eval_file = pd.read_csv(file_path, sep=',')
		for i in list(eval_file.index):
			url = eval_file['url'][i]
			news_content = GetUrlContent(str(url))
			docString = ' '.join(CKIPsegmenter(news_content))
			totalScore, outString = COanalyzer.score(docString)
			print('{} : {} : {}'.format(eval_file['url'][i], eval_file['opi1'][i], totalScore))