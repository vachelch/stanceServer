# coding=utf-8
from flask import Flask, Response, request, render_template
from flask import jsonify
import logging
import jieba

from opinionManager import OpinionManager

app = Flask(__name__, template_folder='app/templates',static_folder='app/static')

manager = OpinionManager(db_path='./OpinionDB/opinion.db', 
						 # w2v_path='./OpinionAnalysis/trainChineseW2V_D300W5MC2_v2.bin')
						 w2v_path='/tmp3/r05922037/embedding/wiki.zh.self.bin')

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

@app.route('/search',methods=['GET'])
# def search():
# 	# Get arguments
# 	text = request.args.get('text')
# 	count = int(request.args.get('count'))

# 	json_data = manager.retrieve(text=text,count=count,core_crawler=2,core_analyzer=2)

# 	# pie_chart_data_sentiment, line_chart_data_sentiment, pie_chart_data_stance, line_chart_data_stance = manager.convert_to_chart_data(json_data)
# 	pie_chart_data_stance, line_chart_data_stance = manager.convert_to_chart_data(json_data)

# 	# return jsonify(pie_chart_dataSentiment=pie_chart_data_sentiment, 
# 	# 			   line_chart_dataSentiment=line_chart_data_sentiment,
# 	# 			   pie_chart_dataStance=pie_chart_data_stance, 
# 	# 			   line_chart_dataStance=line_chart_data_stance)
# 	return jsonify(pie_chart_dataStance=pie_chart_data_stance, 
# 				   line_chart_dataStance=line_chart_data_stance)

@app.route('/list',methods=['GET'])
def list():
	text = request.args.get('text')
	count = int(request.args.get('count'))

	json_data = manager.retrieve(text=text,count=count)
	pie_chart_data_stance, line_chart_data_stance = manager.convert_to_chart_data(json_data)

	return jsonify(json_data=json_data,
				   pie_chart_dataStance=pie_chart_data_stance, 
				   line_chart_dataStance=line_chart_data_stance)

if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
	app.run(host='0.0.0.0', port=6655, debug=True, extra_files=['./app/static/js/index.js'])
