#encoding:  utf-8
import sqlite3

'''
def connect_db():
	try:
		conn = sqlite3.connect('usaco.db')
		print "Opened database successfully";
		return True
	except:
		return False'''

def create_table(sql):
 	try:		
 		conn = sqlite3.connect('usaco.db')
		print "Opened database successfully";
		conn.execute(sql)
		print "Table created successfully";

		conn.close()
		return True
	except:
		return False



def insert_records(sql):
	try:
		conn = sqlite3.connect('usaco.db')
		print "Opened database successfully";

		conn.execute(sql)

		conn.commit()
		print "Records created successfully";
		conn.close()
		return True
	except:
		return False	

def select_records(sql):
	try:
		conn = sqlite3.connect('usaco.db')
		print "Opened database successfully";

		cursor = conn.execute(sql)
		for row in cursor:
		   print "ID = ", row[0]
		   print "NAME = ", row[1]
		   print "url = ", row[2], "\n"

		print "Operation done successfully";
		conn.close()
	except Exception as e:
		return False

def exe_sql(sql):
	try:
		conn = sqlite3.connect('usaco.db')
		print "Opened database successfully";
		conn.execute(sql)
		conn.commit()
		print "Total number of rows updated(deleted) :", conn.total_changes
		conn.close()
		return True
	except Exception as e:
		return False	


sql='''CREATE TABLE contests
(id INT PRIMARY KEY     NOT NULL,
name           CHAR(50)    NOT NULL,
url            TEXT     NOT NULL);'''	

#print create_records(sql)

sql="insert into contests(id,name,url)values(1,'你好','index?2012');"
print insert_records(sql)

sql="SELECT id, name, url  from contests"
print select_records(sql);
#sql="UPDATE contests set name = '2013opens' where ID=1"
#print update_records(sql)

#sql="delete from contests where id=1"
#print exe_sql(sql);
