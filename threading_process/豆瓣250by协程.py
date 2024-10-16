import gevent
from gevent import monkey
monkey.patch_all()
import time
import random
import requests
from lxml import etree
from queue import Queue

class DouBanSpider():
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;WOW64; Trident/7.0;rv:11.0) like Gecko'}
        self.base_url = 'https://movie.douban.com/top250'
        self.dataQueue = Queue()
        self.num = 1
        
    def loadPage(self, url):
        time.sleep(random.random())  # 随机等待，模拟真实请求
        return requests.get(url, headers=self.headers).content
    
    def parsePage(self, url):
        content = self.loadPage(url)  # 修正为调用loadPage，而不是parsePage
        html = etree.HTML(content)
        node_list = html.xpath("//div[@class='info']")
        for node in node_list:
            title = node.xpath(".//span[@class='title']/text()")[0]
            score = node.xpath('.//span[@class="rating_num"]/text()')[0]
            self.dataQueue.put(f"{score}\t{title}")
        
        # 获取下一页链接
        if url == self.base_url:
            next_links = html.xpath("//div[@class='paginator']/a/@href")
            return [self.base_url + link for link in next_links if link != '']  # 确保链接有效
        
    def startWork(self):
        link_list = self.parsePage(self.base_url)
        
        # 创建协程任务并加入队列
        jobs = [gevent.spawn(self.parsePage, link) for link in link_list]
        gevent.joinall(jobs)
        
        # 输出结果
        while not self.dataQueue.empty():
            print(self.num)
            print(self.dataQueue.get())
            self.num += 1
            
if __name__ == '__main__':
    spider = DouBanSpider()
    start = time.time()
    spider.startWork()
    stop = time.time()
    print("\n[LOG]: %f seconds..." % (stop - start))
