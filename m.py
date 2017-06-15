# -*- coding:utf-8 -*-
#import requests
#import bs4

'''
url={"nocow":"http://www.nocow.cn/index.php/USACO_Training",
"usaco_training":"http://train.usaco.org/usacogate",
"usaco_contests":"http://www.usaco.org/index.php?page=contests"}
'''

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

#获取index页,并返回其bs
def getIndex():
	html=saveHtml('index',index_url)
	return BeautifulSoup(html,"lxml")

#获取bs化的html页面内容
def getBsHtml(url):
	response=urllib2.urlopen(base_url+url)
	html=response.read()
	return BeautifulSoup(html,"lxml")

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
			s={"season_name":season}			
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

def main2():
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

	except urllib2.URLError, e:
	    if hasattr(e,"code"):
	        print e.code
	    if hasattr(e,"reason"):
	        print e.reason  

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

			for panel in historypanels:
				pass
			
		except Exception as e:
			pass

def download_prolems(contest_content,contest_dir):		
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
		if not os.path.exists(contest_dir+problem_name+'.html'):#判断是否已下载
			saveHtml(contest_dir+problem_name,problem_url)
			problem_downloaded+=1
		for link in links[1:]:
			url=link["href"]
			file_name=url.split('/')[-1]
			if not os.path.exists(contest_dir+file_name):#判断是否已下载
				saveFileByUrl(file_name,url,contest_dir)
				problem_downloaded+=1

				'''
				if file_name.split('.')[-1]=='zip':
					#urllib.urlretrieve(index_url+url, contest_dir+file_name)
					file={'name':file_name,'url':url}
					print file
					zip_files.append(file)
				else:
					saveFileByUrl(file_name,url,contest_dir)'''

#2014-2015season开始的数据			
def since20142015(season):
	season_name=season["season_name"]
	start_year=season_name[0].split('-')[0].strip()
					
	contests=season["contests"]		
	for contest in contests:
		contest_dir=DIR+season_name[0]+"/"+contest["contest_name"]+"/"
		mkdir(contest_dir)#创建contest目录

		contest_full_url=base_url+contest["contest_url"]			
		file_name=DIR+contest["contest_name"]
		#download and return contest page
		if not os.path.exists(file_name+'.html'):#判断是否已下载
			contest_content=saveHtml(file_name,contest_full_url)
			contest_content=BeautifulSoup(contest_content,"lxml")
		else:
			f=open(file_name+".html","r")	
			contest_content=BeautifulSoup(f.read(),"lxml")
			f.close()

		download_prolems(contest_content,contest_dir)

		'''	
		panels=contest_content.select(".historypanel")	#problem panel

		p_no=0#problem no
		for panel in panels:
			#problem_count=problem_count+1
			p_no+=1
			problem_name=bytes(p_no)+"."+panel.find("b").string
			links=panel.find_all("a")

			#下载题目页面
			problem_url=base_url+links[0]["href"]
			
			cpid=problem_url.split('&')[-1]
			if cpid:					
				problem_name=problem_url.split('&')[-1]+"."+problem_name
			if not os.path.exists(contest_dir+problem_name+'.html'):#判断是否已下载
				saveHtml(contest_dir+problem_name,problem_url)
			
			for link in links[1:]:
				url=link["href"]
				file_name=url.split('/')[-1]
				if not os.path.exists(contest_dir+file_name):#判断是否已下载
					if file_name.split('.')[-1]=='zip':
						#urllib.urlretrieve(index_url+url, contest_dir+file_name)
						file={'name':file_name,'url':url}
						print file
						zip_files.append(file)
					else:
						saveFileByUrl(file_name,url,contest_dir)'''

#2014-2015season以前的数据	
def before20142015(season):
	season_name=season["season_name"]
	start_year=season_name[0].split('-')[0].strip()
		
	contests=season["contests"]
	for contest in contests:
		contest_dir=DIR+season_name[0]+"/"+contest["contest_name"]+"/"
		mkdir(contest_dir)#创建contest目录

		result_url=contest["contest_url"]			
		file_name=DIR+contest["contest_name"]
		

		result_content=getBsHtml(result_url)
		contest_full_url=base_url+result_content.select(".panel a")[0]['href']
		
		#download and return contest page
		if not os.path.exists(file_name+'.html'):#判断是否已下载
			print "download:"+file_name
			contest_content=saveHtml(file_name,contest_full_url)
			contest_content=BeautifulSoup(contest_content,"lxml")
		else:
			f=open(file_name+".html","r")	
			contest_content=BeautifulSoup(f.read(),"lxml")
			f.close()

		download_prolems(contest_content,contest_dir)	

def download(seasons):
	for season in seasons:		
		season_name=season["season_name"]
		
		log_handler.write(season_name+"\n")

		start_year=season_name[0].split('-')[0].strip()

		mkdir(DIR+season_name[0])#创建season目录
		contests=season["contests"]

		
		if start_year>='2014':
			since20142015(season)
		else:	
			before20142015(season)




def output(list):
	f=open('down_zip.txt','wb')
	for item in list:
		f.write(base_url+item['url']+"\n")
	f.close()	

def main():
	log_handler=open(log_file,"wb")
	index=getIndex()
	seasons=getSeasons(index)
	mkdir(DIR)
	download(seasons)
	#output(zip_files)
	print problem_count
	print problem_downloaded
	log_handler.close()

if __name__ == '__main__':
    main()
    