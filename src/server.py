# coding=utf-8
from flask import Flask, Response, request, render_template
from flask import jsonify
import logging
import jieba
import json
import time

from global_set import load_static
from opinionManager import OpinionManager
from NewsCrawler import GetUrlContent

app = Flask(__name__, template_folder='app/templates',static_folder='app/static')

global_set = load_static()

manager = OpinionManager(db_path='./OpinionDB/opinion.db', 
						 w2v_path='/tmp3/r05922037/embedding/wiki.zh.self.bin',
						 global_set = global_set)

def JIEBAInit(file_path='OpinionAnalysis/dict/'):
	logging.info('Loading dictionary and initializing jieba...')
	jieba.set_dictionary(file_path+'dict.txt.big')
	jieba.load_userdict(file_path+'userdict.txt')
	jieba.initialize()

print("Init JIEBA")
JIEBAInit('OpinionAnalysis/dict/')
print("Init JIEBA Finished!")

@app.route('/')
def homepage():
	return render_template("index.html")

@app.route('/data.html')
def data():
	return render_template("data.html")

@app.route('/list',methods=['GET'])
def list():
	text = request.args.get('text')
	count = int(request.args.get('count'))

	print(text, count)
	start = time.time()
	json_data = manager.retrieve(text=text,count=count)
	pie_chart_data_stance, line_chart_data_stance = manager.convert_to_chart_data(json_data)

	print("total time: %f s"%(time.time() - start))
	return jsonify(json_data=json_data,
				   pie_chart_dataStance=pie_chart_data_stance, 
				   line_chart_dataStance=line_chart_data_stance)


@app.route('/feedback',methods=['POST', 'GET'])
def feedback():
	if request.method == 'POST':
		dataDict = request.values
		# for requests
		# dataDict = json.loads(request.data.decode('utf8'))

		operation = dataDict.get('operation')
		query = dataDict.get('query')
		url = dataDict.get('url')
		title = dataDict.get('title')
		website = dataDict.get('website')
		date = dataDict.get('date')
		stance = dataDict.get('stance')
		label = dataDict.get('label')

		if operation == 'insert':
			in_db_urls, urls = manager.db.filter([url])
			if len(urls) > 0:
				content = GetUrlContent(url)
				manager.db.insert([[query, url, title, website, date, stance, label, content]])
				return 'inserted'
			else:
				return 'already in database'

		elif operation == 'delete':
			manager.db.delete([[url]])
			return 'deleted'

		elif operation == 'update':
			manager.db.update([[stance, label, url]])
			return 'updated'

	elif request.method == 'GET':
		json_data = manager.retrieve_from_local()
		print(json_data[94])
		return json.dumps(json_data)

	return 'invalid operation'


if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
	app.run(host='0.0.0.0', port=6655, debug=True, extra_files=['./app/static/js/index.js'])



















