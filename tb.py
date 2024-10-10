import requests
import re
import time
import random
import os

class TiebaSpider:
    def __init__(self):
        """初始化参数"""
        self.kw = input('关键词>')
        self.base_url = 'https://tieba.baidu.com/f'
        self.page_num = 1
        self.title = ''


    def parse_text(self, url, params=None):
        """发送请求，获取响应内容"""
        # 休眠，防止对面反爬探测
        time.sleep(random.randint(1, 5))
        req = requests.get(url, params=params)
        return req.text

    def page(self, content):
        """解析每一页"""
        print('在第{}页爬取中...'.format(self.page_num))
        self.page_num += 1
        url_title = re.findall(
            r'<a rel="noopener" href="(/p/\d+?)" title=".+?" target="_blank" class="j_th_tit ">(.+?)</a>', content)
        for url, title in url_title:
            self.title = title
            self.detail('https://tieba.baidu.com' + url)
            # 保存标题
            self.save_title()
        # 判断下一页
        next_url = re.findall(r'<a href="(.*?)" .*>下一页</a>', content)
        if next_url:
            next_url = 'https:' + next_url[0]
            content = self.parse_text(url=next_url)
            self.page(content)
        else:
            print("爬虫结束...")

    def detail(self, url):
        """每一个帖子的详情"""
        content = self.parse_text(url=url)
        urls = re.findall(r'<img class="BDE_Image".*?src="(.*?)".*?>', content)

 
    def save_title(self):
        """保存帖子的标题"""
        with open('./data/tieba/tieba_{}.txt'.format(self.kw), 'a', encoding='utf-8') as file:
            file.write(self.title)
            file.write('\n')


    def start(self):
        """开始咯"""
        print("紧张又刺激爬虫环节")
        content = self.parse_text(url=self.base_url, params={'kw': self.kw, 'ie': 'utf-8', 'fr': 'search'})
        self.page(content)

if __name__ == '__main__':
    spider = TiebaSpider()
    spider.start()