import time
import random
import requests
import multiprocessing
from lxml import etree
from multiprocessing import Queue, Manager

# 独立的解析函数，不依赖类实例
def parsePage(url, headers, dataQueue):
    session = requests.Session()  # Create session here
    time.sleep(random.uniform(1, 3))  # Adjusted for better delay
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
        content = response.content
    except requests.RequestException as e:
        print(f"ERROR loading {url}: {e}")
        return

    html = etree.HTML(content)
    node_list = html.xpath("//div[@class='info']")
    for node in node_list:
        title = node.xpath(".//span[@class='title']/text()")
        score = node.xpath('.//span[@class="rating_num"]/text()')
        
        if title and score:
            dataQueue.put(f"{score[0]}\t{title[0]}")

    # Return links for pagination if it's the first page
    if url == 'https://movie.douban.com/top250':
        return ['https://movie.douban.com/top250' + link for link in html.xpath("//div[@class='paginator']/a/@href") if 'start' in link]

class DouBanSpider:
    """Multi-process web scraper for DouBan Top 250 movies."""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"
        }
        self.baseUrl = 'https://movie.douban.com/top250'
        self.manager = Manager()
        self.dataQueue = self.manager.Queue()
        self.num = 1
        
    def startWork(self):
        # 使用独立的函数进行页面解析，传递必要的参数
        link_list = parsePage(self.baseUrl, self.headers, self.dataQueue)
        if not link_list:
            print("No additional links found.")
            return
        
        process_list = []
        
        # Create and start processes for each link
        for link in link_list:
            process = multiprocessing.Process(target=parsePage, args=(link, self.headers, self.dataQueue))
            process.start()
            process_list.append(process)

        # Wait for all processes to finish
        for process in process_list:
            process.join()

        # Print the collected data
        while not self.dataQueue.empty():
            print(self.num)
            print(self.dataQueue.get())
            self.num += 1

if __name__ == '__main__':
    spider = DouBanSpider()
    start = time.time()
    spider.startWork()
    stop = time.time()
    print(f"\n[LOG]: {stop - start:.2f} seconds...")
