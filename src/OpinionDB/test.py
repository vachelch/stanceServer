import sqlite3
from urllib.parse import unquote
import numpy as np
import csv

db_path = 'opinion.db'
db_path2 = 'opinion2.db'

create_table_stmt ="""
CREATE TABLE IF NOT EXISTS opinion
(
query VARCHAR(255),
url VARCHAR(255) NOT NULL,
title VARCHAR(255),
website VARCHAR(255),
date DATE,
stance VARCHAR(10),
label VARCHAR(10),
content VARCHAR(4096)
);
"""

drop_table_stmt = """DROP TABLE IF EXISTS opinion;"""
describe_table_stmt = """PRAGMA table_info(opinion);"""
insert_stmt = "INSERT INTO opinion (query, url, title, website, date, stance, label, content) VALUES (\"{}\", \"{}\", \"{}\", \"{}\", \"{}\", \"{}\", \"{}\" ,\"{}\");"
delete_stmt = "DELETE FROM opinion WHERE url=\"{}\""
update_stmt = "UPDATE opinion SET stance=\"{}\",label=\"{}\" where url=\"{}\""
check_stmt = "SELECT EXISTS(SELECT 1 FROM opinion WHERE url=\"{}\" LIMIT 1);"
select_url_stmt = "SELECT * FROM opinion WHERE url=\"{}\" LIMIT 1"
select_all_stmt = "SELECT * FROM opinion"

# raw data
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()
cursor.execute(select_all_stmt)
raw_data = cursor.fetchall()

# new table
conn2 = sqlite3.connect(db_path2, check_same_thread=False)
cursor2 = conn2.cursor()

raw_data = [row for row in raw_data if row[0] != '']

feedback = []
stances = set(['贊成', '支持', '反對'])

for i, row in enumerate(raw_data):
	label = row[6]
	query = row[0]
	content = " ".join([row[2].strip(), row[7].strip()])

	if query[:2] not in stances:
		query = '贊成' + query

	if label == 'neutral':
		label = 'discuss'
	
	feedback.append([label, query, content])


with open('train_feedback.csv', 'w') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',')
    for row in feedback:
    	spamwriter.writerow(row)
    






























