import json
import sqlite3
import logging

# Sql Statements
create_table_stmt ="""
CREATE TABLE IF NOT EXISTS opinion
(
url VARCHAR(255) NOT NULL,
title VARCHAR(255),
t_sentiment VARCHAR(10),
t_score FLOAT(8),
sentiment VARCHAR(10),
score FLOAT(8),
source VARCHAR(255),
date DATE,
stance VARCHAR(10)
);
"""
drop_table_stmt = """DROP TABLE IF EXISTS opinion;"""
describe_table_stmt = """PRAGMA table_info(opinion);"""
insert_stmt = "INSERT INTO opinion (url, title, t_sentiment, t_score, sentiment, score, source, date, stance) VALUES (\"{}\", \"{}\", \"{}\", {}, \"{}\", {}, \"{}\", \"{}\", \"{}\");"
check_stmt = "SELECT EXISTS(SELECT 1 FROM opinion WHERE url=\"{}\" LIMIT 1);"
select_url_stmt = "SELECT * FROM opinion WHERE url=\"{}\" LIMIT 1"
select_all_stmt = "SELECT * FROM opinion"

class OpinionDB(object):
	def __init__(self, db_path='opinion.db'):
		self.conn = sqlite3.connect(db_path, check_same_thread=False)
		self.cursor = self.conn.cursor()

		# By default create table
		self._create_table(drop=False)

	def __del__(self):
		self.conn.close()

	def _create_table(self, drop=False):
		if drop is True:
			self.cursor.execute(drop_table_stmt)
		self.cursor.execute(create_table_stmt)
		self.conn.commit()

	def _describe_table(self):
		self.cursor.execute(describe_table_stmt)
		print(self.cursor.fetchall())


	def insert(self, data):
		for row in data:
			try:
				self.cursor.execute(insert_stmt.format(*row))
			except:
				logging.warning('sqlite3.OperationalError')
		self.conn.commit()

	def filter(self,urls):
		exist_urls = []
		not_exist_urls = []
		for url in urls:
			self.cursor.execute(check_stmt.format(url))
			url_exists = self.cursor.fetchone()[0] # 1, 0
			if url_exists:
				exist_urls.append(url)
			else:
				not_exist_urls.append(url)

		return exist_urls, not_exist_urls

	def select_url(self, url):
		print(url)
		self.cursor.execute(select_url_stmt.format(url))
		row = self.cursor.fetchone()
		return row

	def show_all(self):
		self.cursor.execute(select_all_stmt)
		print(self.cursor.fetchall())
'''
if __name__ == "__main__":

    db = OpinionDB(db_path='example.db')

    db._create_table(drop=True)
    db._describe_table()

    test_data = create_test_data()
    db.insert(test_data)

    urls = ['\"http://news.ltn.com.tw/news/politics/paper/1111059\"', '\"url2\"']
    print(db.filter(urls))

    db.show_all()
'''