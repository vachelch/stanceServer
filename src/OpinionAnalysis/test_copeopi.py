from GetOpinion import CopeOpiAnalyzer, read_text
import pandas as pd

if __name__ == '__main__':
	outcsv = pd.read_csv('CopeOpi t.csv', header = None)
	orin = outcsv[1].tolist()

	COanalyzer = CopeOpiAnalyzer('CopeOpi/dic_trad/')
	mine = list()
	for i in range(50):	
		docString = read_text('../../data/'+str(i)+'.txt')
		totalScore, outString = COanalyzer.score(docString)
		mine.append(totalScore)

	for i in range(50):
		if mine[i] != orin[i]:
			docString = read_text('../../data/'+str(i)+'.txt')
			totalScore, outString = COanalyzer.score(docString)
			print('doc {}. score = {} & {}'.format(i, mine[i], orin[i]))
			print(outString)
			docString = read_text('CopeOpi/out/'+str(i)+'.txt', False)
			print(docString)

 
from ckipsvr import CKIPsegmenter
from getOpinion import CopeOpiAnalyzer
from getNews import GetUrlContent
# import jieba
# from nltk.tag import StanfordPOSTagger
# from Analysis import Stanford2CKIP
# SFtagger = StanfordPOSTagger('StanfordPosTagger/models/chinese-distsim.tagger','StanfordPosTagger/stanford-postagger-3.7.0.jar')

COanalyzer = CopeOpiAnalyzer('CopeOpi/dic_trad/')
news_url = 'https://newtalk.tw/news/view/2017-06-23/90144'
news_content = GetUrlContent(news_url)
seg_output = CKIPsegmenter(news_content)
seg_output = ' '.join(seg_output)
totalScore, outString = COanalyzer.score(seg_output)
print(outString)


news_url = 'https://newtalk.tw/news/view/2017-06-23/90144'
news_content = GetUrlContent(news_url)
seg_output = list(jieba.cut(news_content.replace('\xa0',' ')))
stanford_output = SFtagger.tag(seg_output)
news_content = ''
for out in stanford_output:
	news_content += out[1].split('#')[0] + '(' + Stanford2CKIP(out[1].split('#')[1]) + ') '

totalScore, outString = COanalyzer.score(news_content)
print(outString)


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
		print('key "{}" does not exist in Stanford2CKIP mapping.'.format(x))
		return(x)
