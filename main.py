# -*- coding:utf-8 -*-
#import requests
#import bs4

'''
url={"nocow":"http://www.nocow.cn/index.php/USACO_Training",
"usaco_training":"http://train.usaco.org/usacogate",
"usaco_contests":"http://www.usaco.org/index.php?page=contests"}
'''

url="http://www.usaco.org/index.php?page=contests";
base_url="http://www.usaco.org/"
import urllib2  
import bs4
from bs4 import BeautifulSoup  
import re
import db_sqlite

def contest_exist(contest_name):
	
	conn = db_sqlite.get_conn(DB_FILE_PATH)
	sql="select * from contests where name='"+contest_name+"'"
	return db_sqlite.fetchrecords(conn,sql)
def addcontest(contest_name,contest_url):
	save_sql = '''INSERT INTO contests(name,url) values (?,?)'''
	data = [(contest_name, contest_url)]
	conn = db_sqlite.get_conn(DB_FILE_PATH)
	db_sqlite.save(conn, save_sql, data)


def filter_node(item):
	if type(item)==bs4.element.NavigableString:
		return False
	elif type(item)==bs4.element.Tag:
		contest=item.find('a')
		if contest:#link to contest
			contest_name=item.a.string	
			contest_url=item.a['href']
			download_pages.append(contest_url)
			if not contest_exist(contest_name):				
				addcontest(contest_name,contest_url)
			#print contest_name+":"+base_url+contest_url

			return True
	return False
	
	'''pattern = re.compile('<p>.*<a.* href=".*">.*</a>.*</p>',re.S)	
	result= re.findall(pattern,item)
	print result'''
def saveHtml(file_name, file_content):  
    #    注意windows文件命名的禁用符，比如 /  
    with open(file_name.replace('/', '_') + ".html", "wb") as f:  
        #   写文件用bytes而不是str，所以要转码  
        f.write(file_content)  

def main():
	#本次需要下载的页面
	global download_pages
	download_pages=[]
	#数据库文件
	global DB_FILE_PATH
	DB_FILE_PATH='usaco.db'
	#是否打印sql
	global SHOW_SQL
	SHOW_SQL = False

	try:
		response = urllib2.urlopen(url)
		content = BeautifulSoup(response.read(),"lxml")

		h2s=content.select('div[class="panel"] h2')
		
		for h2 in h2s:

			pattern=re.compile('.*Previous Contests:(.*Season).*',re.S)		
			season = re.findall(pattern,h2.string)
			
			if len(season)>0:
				#print season
				sibling=h2.find_next_sibling()
				
				while filter_node(sibling):				
					sibling=sibling.find_next_sibling()
					
				
				#while type(sibling)==bs4.element.Comment:
				
		#print content.select('div[class="panel"] p a')

		'''pattern = re.compile('<p>.*<a.* href=".*">.*</a>.*</p>',re.S)
		
		items = re.findall(pattern,content)
		print items
		for item in items:
			print item	'''
	except urllib2.URLError, e:
	    if hasattr(e,"code"):
	        print e.code
	    if hasattr(e,"reason"):
	        print e.reason  
	#print download_pages

	for page in download_pages[:1]:
		try:
			print page
			response = urllib2.urlopen(base_url+page)

			content = BeautifulSoup(response.read(),"lxml")
			print type(content)

			groups=content.select("h2 img")
			for g in groups:
				group=g.parent
				print group
				print type(group)

				for i in group:
					print i

				historypanels=group.select('.historypanel')
				print historypanels	

			
			historypanels=content.select('.historypanel')#select('div[class="panel historypanel"]')
			#print len(historypanels)

			for panel in historypanels:
				#print panel
				pass
				
			
			#print historypanels
			
			
		except Exception as e:
			pass


if __name__ == '__main__':
    main()
    #print contest_exist('2016')