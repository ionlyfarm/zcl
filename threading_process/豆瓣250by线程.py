import requests
import random
import time
import threading
from lxml import etree
from queue import Queue

class DouBanSpider():
    """多线程爬虫"""
    
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"}
        self.base_url = "https://movie.douban.com/top250"
        self.dataQueue = Queue()
        self.num = 1
        self.session = requests.Session()
        self.lock = threading.Lock()
        
    def loadPage(self, url):
        time.sleep(random.random())
        try:
            response = self.session.get(url, headers=self.headers) #可以在请求之中保持某些参数，并且可以提高效率
            response.raise_for_status() #进行错误检查
            return response.content
        except requests.RequestException as e:
            print(f"Error loading {url}: {e}")
            return None
    
    def parsePage(self, url):
        content = self.loadPage(url)
        if content is None:
            return []
        
        html = etree.HTML(content)
        node_list = html.xpath("//div[@class='info']")
        for node in node_list:
            title = node.xpath(".//span[@class='title']/text()")[0]
            score = node.xpath('.//span[@class="rating_num"]/text()')[0]
            with self.lock:
                self.dataQueue.put(f"{score}\t{title}")
        #将线程锁上，保证数据传输安全
        if url == self.base_url:
            return [self.base_url + link for link in html.xpath("//div[@class='paginator']/a/@href")]
        return []
            
    def startWork(self):
        link_list = self.parsePage(self.base_url)
        thread_list = []
        for link in link_list:
            thread = threading.Thread(target=self.parsePage, args=[link])
            thread.start()
            thread_list.append(thread)
        for thread in thread_list:
            thread.join()
            
        while not self.dataQueue.empty():
            print(self.num)
            print(self.dataQueue.get())
            self.num += 1
            
if __name__ == '__main__':
    spider = DouBanSpider()
    start = time.time()
    spider.startWork()
    stop = time.time()
    print(f"\n[LOG]: {stop - start:.6f} seconds...")