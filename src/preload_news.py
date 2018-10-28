from opinionManager import OpinionManager
import logging

if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
	manager = OpinionManager(db_path='./OpinionDB/opinion.db')

	kw_list = ['年金改革', '一例一休', '巴拿馬', '巴拿馬斷交', '趙藤雄', '柯文哲', '川普', '台積電', '世大運']
	for text in kw_list:
		json_data = manager.retrieve(text=text,count=100,core_crawler=20,core_analyzer=2)