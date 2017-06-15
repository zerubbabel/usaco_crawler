# -*- coding:utf-8 -*-
#import requests
#import bs4

'''
url={"nocow":"http://www.nocow.cn/index.php/USACO_Training",
"usaco_training":"http://train.usaco.org/usacogate",
"usaco_contests":"http://www.usaco.org/index.php?page=contests"}
'''
# 爬取usaco保存成txt文档然后利用下载根据如uget下载

index_url="http://www.usaco.org/index.php?page=contests";
base_url="http://www.usaco.org/"

files=[]
download_pages=[]
zip_files=[]
#global problem_count,problem_downloaded
problem_count=0
problem_downloaded=0
DB_FILE_PATH='usaco.db'
DIR="archives/"
import urllib2  
import bs4
from bs4 import BeautifulSoup  
import re
import db_sqlite
import os
import urllib 
import requests
import time
log_file=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))+'_log.txt'

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
		return None
	elif type(item)==bs4.element.Tag:
		contest=item.find('a')
		if contest:#link to contest
			contest_name=item.a.string	
			contest_url=item.a['href']
			download_pages.append(contest_url)					
			return {"contest_name":contest_name,"contest_url":contest_url}
	return None
	
	'''pattern = re.compile('<p>.*<a.* href=".*">.*</a>.*</p>',re.S)	
	result= re.findall(pattern,item)
	print result'''

#生成路径
def mkdir(path):
    # 引入模块
    import os
 
    # 去除首位空格
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\")
 
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists=os.path.exists(path)
 
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path) 
 
        #print path+' 创建成功'
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        #print path+' 目录已存在'
        return False

#根据url保存html文件并返回content	
def saveHtml(file_name,url):  
	try:
		response = urllib2.urlopen(url)
		file_content=response.read()
		#    注意windows文件命名的禁用符，比如 /  
		#with open(file_name.replace('/', '_') + ".html", "wb") as f:
			#   写文件用bytes而不是str，所以要转码  
			#f.write(file_content)
		f=open(file_name+".html","wb")	
		f.write(file_content)
		f.close()
		return file_content   
	except urllib2.URLError, e:
		if hasattr(e,"code"):
		    print e.code
		if hasattr(e,"reason"):
		    print e.reason	

#根据url直接保存文件
def saveFileByUrl(file_name,url,directory):
	try:
		#print "starting download:"+url
		response=urllib2.urlopen(base_url+url)
		html=response.read()		
		f=open(directory+file_name,"wb")
		f.write(html)
		f.close()
	except urllib2.URLError, e:
		if hasattr(e,"code"):
		    print e.code
		if hasattr(e,"reason"):
		    print e.reason 

'''
	数据格式
	seasons={
		"season_name":"2011-2012 Season",
		"contests":[
			{'contest_url': 'index.php?page=open12results', 
			'contest_name': u'2012 US Open Contest Results'},
			{'contest_url': 'index.php?page=mar12results', 
			'contest_name': u'2012 March Contest Results'}
		]
	}
'''	
def getSeasons(content):
	seasons=[]
	h2s=content.select('div[class="panel"] h2')	
	for h2 in h2s:
		pattern=re.compile('.*Previous Contests:(.*Season).*',re.S)		
		season = re.findall(pattern,h2.string)

		if len(season)>0:
			s={"season_name":season[0]}			
			sibling=h2.find_next_sibling()
			contests=[]
			while True:
				contest=filter_node(sibling)
				if contest==None:break
				sibling=sibling.find_next_sibling()
				contests.append(contest)				
			s["contests"]=contests
			seasons.append(s)				
	return seasons


def download_prolems(contest_content,contest_dir):	
	problems=[]	
	panels=contest_content.select(".historypanel")	#problem panel

	p_no=0#problem no
	for panel in panels:
		global problem_downloaded,problem_count
		problem_count+=1
		p_no+=1
		problem_name=bytes(p_no)+"."+panel.find("b").string.replace('/', '_')
		links=panel.find_all("a")

		#下载题目页面
		problem_url=base_url+links[0]["href"]
		
		cpid=problem_url.split('&')[-1]
		if cpid:					
			problem_name=problem_url.split('&')[-1]+"."+problem_name
		filename=contest_dir+problem_name+'.html'	
		#outputToFile(filename,problem_url)
			
		if not os.path.exists(contest_dir+problem_name+'.html'):#判断是否已下载
			saveHtml(contest_dir+problem_name,problem_url)
			problem_downloaded+=1

		for link in links[1:]:
			url=link["href"]
			file_name=url.split('/')[-1]
			#outputToFile(contest_dir+file_name,base_url+url)
			
			if not os.path.exists(contest_dir+file_name):#判断是否已下载
				saveFileByUrl(file_name,url,contest_dir)
				problem_downloaded+=1
		'''		
		problem={'name':problem_name,'url':problem_url,
			'data_url':links[1]["href"],
			'sol_url':links[2]["href"]}
		problems.append(problem)'''
	return problems				


def output(list):
	f=open('down_zip.txt','wb')
	for item in list:
		f.write(base_url+item['url']+"\n")
	f.close()	

#时间戳
def timestamp():
	return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

#输出内容到文件
def outputToFile(filename,content):
	if not os.path.exists(filename):
		f=open(filename,"wb")
		f.write(content)
		f.close()
	else:
		print filename+" already exist!"	

#获取html页面内容
def getHtml(url):
	print "download:"+url
	return urllib2.urlopen(url).read()
#bs化Html
def bsHtml(html):
	return BeautifulSoup(html,"lxml")

#读取文件
def readFile(filename):
	f=open(filename,"r")
	content=f.read()
	f.close()
	return content

#生成所有season的html
def makeSeasonHtml(seasons):
	html=""
	for s in seasons:
		html+="<h2>"+s["season_name"]+"</h2>"
		for c in s['contests']:
			html+="<p><a href='"+c['contest_url']+"'>"+c['contest_name']+"</a></p>"
	tpl=readFile('index.tpl')
	indexHtml=tpl % html
	outputToFile('home.html',indexHtml)

def download_contest(filename,url):
	#download and return contest page
	if not os.path.exists(filename+'.html'):#判断是否已下载
		html=getHtml(url)
		outputToFile(filename,html)
		contest_content=bsHtml(html)
	else:
		contest_content=bsHtml(readFile(filename))
	return contest_content	

def getContests(seasons):
	for season in seasons:		
		season_name=season["season_name"]
		start_year=season_name.split('-')[0].strip()
		season_dir=DIR+season_name
		mkdir(season_dir)#创建season目录	
		contests=season["contests"]

		for contest in contests:
			contest_dir=season_dir+"/"+contest["contest_name"]+"/"
			mkdir(contest_dir)#创建contest目录
			

			file_name=DIR+contest["contest_name"]
			print start_year
			#处理2013-2014season之前的不同情况
			if start_year>='2014': 
				contest_full_url=base_url+contest["contest_url"]
			else:	
				result_url=contest["contest_url"]			
				result_content=bsHtml(getHtml(base_url+result_url))
				contest_full_url=base_url+result_content.select(".panel a")[0]['href']
											
			contest_content=download_contest(file_name,contest_full_url)				
			problems=download_prolems(contest_content,contest_dir)
			#makeContestHtml(contest_dir,contest,problems)	

def main():
	indexHtml=getHtml(index_url)
	seasons=getSeasons(bsHtml(indexHtml))	
	mkdir(DIR)
	contests=getContests(seasons)
	makeSeasonHtml(seasons)

def testPrintDir(dir):
	print dir

if __name__ == '__main__':
    main()
    