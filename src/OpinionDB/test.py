import sqlite3

db_path = 'opinion.db'

conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()

select_all_stmt = "SELECT url, title, website, date, stance, label FROM opinion"
insert_stmt = "INSERT INTO opinion (url, title, t_sentiment) VALUES ('a', 'b', '12345678910');"
delete_stmt = "DELETE FROM opinion WHERE title='航港局基本時薪大幅調高至19元';"

#cursor.execute(delete_stmt)
#conn.commit()
cursor.execute(select_all_stmt)
print(cursor.fetchall())


