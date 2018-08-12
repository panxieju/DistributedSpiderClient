#!usr/bin/python
# -*- coding:utf-8 -*-
'''
Created on 2017年3月20日

@author: Administrator
'''
import random
from urllib.request import Request
from urllib.request import urlopen
import gzip
import re

import requests


class Downloader(object):
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]

    def get_random_agent(self):
        return random.choice(self.user_agent_list)

    def download(self, url):
        requests.packages.urllib3.disable_warnings()
        req = Request(url, headers={'User-Agent': self.get_random_agent(), })
        try:
            html = urlopen(req).read()
            return html
        except:
            try:
                if re.search(r'http://jxjump.58.com/.*', url):
                    url = url.split('&')[0]
                    req = Request(url, headers={'User-Agent': 'Mozilla/5.0', })
                    html = urlopen(req).read()
                    return html
            except:
                print("无法下载详情页面", url)
            pass

    def download_gzip(self, url):
        if url is None:
            return None
        try:
            response = urlopen(url).read()
        except:
            print('响应错误', url)
            return None
        html = gzip.decompress(response)
        return html.decode('gbk')

    def anjuke_downloader(self, url):
        authority = url.split('//')[1].split('/')[0]
        path = url.split('//')[1].split('com')[1].split('#')[0]
        print(authority, path)
        header = {
            ':method': 'GET',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36',
            'upgrade-insecure-requests:': '',
            'cookie': 'sessid=30DF35AB-447B-EDA2-6B4C-B7FA5986F762; als=0; lps=http%3A%2F%2Fsh.zu.anjuke.com%2Ffangyuan%2F1073106787%7C; ctid=11; __xsptplusUT_8=1; propertys=hqwehv-osvwde_; __xsptplus8=8.8.1499705665.1499705763.3%232%7Cbzclk.baidu.com%7C%7C%7Canjuke%7C%23%23xjOIT6pSdU7g4wQT6W_zfMSuNyC8W2M2%23; _ga=GA1.2.1333292372.1498739618; _gid=GA1.2.1585126968.1499705666; _gat=1; aQQ_ajkguid=2A042F27-4958-ED45-76A0-0171165AF2E4; twe=2; 58tj_uuid=c48c209b-84be-402d-ae2d-65d368ab7bc1; new_session=0; init_refer=; new_uv=8',
            'referer': 'https://www.anjuke.com/captcha-verify/?callback=shield&from=antispam&history=aHR0cHM6Ly9zaC56dS5hbmp1a2UuY29tL2Zhbmd5dWFuLzEwNzMxMDY3ODc%3D',
            'cache-control': 'max-age=0',
            'accept-language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,zh-TW;q=0.2',
            'accept-encoding': 'gzip, deflate, br',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            ':scheme': 'https',
            ':path': path,
            ':authority': authority
        }
        import requests
        import scrapy
        response = requests.get(url, headers=header, verify=True)
        return scrapy.http.HtmlResponse(status=response.status_code, body=response.content,
                                        url=response.url)

    def download_html_response(self, url):
        import requests
        import scrapy
        header = {'User-Agent': self.get_random_agent(), }
        response = requests.get(url, headers=header, verify=False)
        return scrapy.http.HtmlResponse(status=response.status_code, body=response.content,
                                        url=response.url)

    def download_https_response(self, url):
        import requests
        import scrapy
        header = {'User-Agent': self.get_random_agent(), }
        response = requests.get(url, headers=header, verify=False)
        return scrapy.http.HtmlResponse(status=response.status_code, body=response.content,
                                        url=response.url)

    def download_fang(self, url):
        import requests
        import scrapy
        header = {'User-Agent': self.get_random_agent(),
                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                  'Accept-Encoding': 'gzip, deflate',
                  'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,zh-TW;q=0.2',
                  'Cache-Control': 'max-age=0',
                  'Connection': 'keep-alive',
                  # 'Host':'zu.fang.com',
                  'Referer': 'http://www.fang.com/',
                  'Upgrade-Insecure-Requests': '1',
                  }
        response = requests.get(url, headers=header, verify=False)
        return scrapy.http.HtmlResponse(status=response.status_code, body=response.content,
                                        url=response.url)


if __name__ == '__main__':
    downloader = Downloader()
    '''
    response = downloader.download("https://www.anjuke.com")
    html = response.decode('utf-8')
    if re.search('访问验证', html):
        print('遇到反爬机制了')
        '''

    from bs4 import BeautifulSoup as Soup

    url = ' https://gz.zu.anjuke.com/fangyuan/1167213348'
    content = downloader.anjuke_downloader(url)
    html = Soup(content.body, "html.parser")
    print(html.prettify())
