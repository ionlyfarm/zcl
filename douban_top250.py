import requests
import time
import random
from lxml import etree
from queue import Queue

class DoubanSpider():
    def __init__(self):
        #设置请求头，模拟浏览器
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0;WOW64; Trident/7.0;rv:11.0) like Gecko'}
        self.base_url = 'https://movie.douban.com/top250'
        #以队列的形式
        self.dataQueue = Queue()
        #num数字编号
        self.num = 1
        
    def loadPage(self,url):
        time.sleep(random.randint(1,5))
        return requests.get(url=url,headers=self.headers).content
    
    def parsePage(self,url):
        content = self.loadPage(url)
        html = etree.HTML(content)
        node_list = html.xpath("//div[@class='info']")
        for node in node_list:
            title = node.xpath(".//span[@class='title']/text()")[0]
            score = node.xpath(".//span[@class='rating_num']/text()")[0]#/text()表示要提取文本内容
            #将数据存入队列当中
            self.dataQueue.put(score+'\t'+title)
        if url == self.base_url:
            #只有第一页才获取url组成的列表，其他页就不再获取
            return [self.base_url + link for link in html.xpath("//div[@class='paginator']/a/@href")]
        
    def startWork(self):
        link_list = self.parsePage(self.base_url)
        for link in link_list:
            self.parsePage(link)
            
        while not self.dataQueue.empty():
            print(self.num)
            print(self.dataQueue.get())
            self.num += 1
            
if __name__ == '__main__':
    spider = DoubanSpider()
    start = time.time()
    spider.startWork()
    stop = time.time()
    print("\n[LOG]: %f seconds..."%(stop-start))