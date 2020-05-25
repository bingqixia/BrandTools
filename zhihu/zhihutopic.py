# -*- coding: utf-8 -*-
import requests
import execjs
import time
from http import cookiejar 
from urllib import parse
import json
from zhihulogin import ZhihuAccount

class Topic(object):

    def __init__(self,keyword):
        self.timestamp = int(time.time() * 1000)
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
            'content-type': 'application/json',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'cache-control': 'no-cache, no-store, must-revalidate, private, max-age=0',
            'pragma': 'no-cache',
            'referer':'https://www.zhihu.com/search?type=topic&q=%s' % parse.quote(keyword),
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'x-api-version': '3.0.91',
            'x-app-za': 'OS=Web',
            'x-requested-with': 'fetch',
            'x-zse-83': '3_2.0'
        }
        self.session = requests.session()
        self.session.cookies = cookiejar.MozillaCookieJar('cookies.txt')
        self.keyword = keyword
   
    def __get_value(self, e):
        with open('./x_zse_86.js') as f:
            js = execjs.compile(f.read())
            e = js.call('q', e)
        with open('./encrypt.js') as f:
            js = execjs.compile(f.read()) 
            ret = js.call('b', e)
            return ret

    def get_zse86(self, d_c: str = None):
        K = "1.0"
        web = '3_2.0'   
        url = 'https://www.zhihu.com/search?type=topic&q=%s' % parse.quote(self.keyword)    
        search_api = '/api/v4/search_v3?t=topic&q=%s&correction=1&offset=0&limit=20&lc_idx=0&show_all_topics=1' % parse.quote(self.keyword)
        f = "+".join((web, search_api, url, d_c))
        signature = self.__get_value(f)
        x_zse_86 = K + "_" + signature
        return x_zse_86

    #get topic_id which matchs keyword
    def get_topic_url(self):
        time.sleep(3)
        topic_url = ''
        url = 'https://www.zhihu.com/api/v4/search_v3?t=topic&q=%s&correction=1&offset=0&limit=20&lc_idx=0&show_all_topics=1' % (parse.quote(self.keyword))
        self.session.cookies.load()
        cookies_dict = requests.utils.dict_from_cookiejar(self.session.cookies)

        d_c0 = cookies_dict['d_c0']
        x_zse_86 = self.get_zse86(d_c0)
        self.headers['x-zse-86'] = x_zse_86
    
        # json_data = self.session.get(url, headers=self.headers, verify=False).json()
        json_data = self.session.get(url, headers=self.headers).json()
        self.keyword = self.keyword.replace("＆", "&")
        if 'data' in json_data:
            topic_datas = json_data['data']

            if len(topic_datas) == 0:
                print('搜索结果为空')
                return topic_url

            topic_data = topic_datas[0]

            if (not 'id' in topic_data) or (not 'object' in topic_data):
                return topic_url

            topic_id = topic_data['id']
            topic_aliases = topic_data['object']['aliases']
            topic_aliases = [x.lower() for x in topic_url]

            print('topic_aliases: %s' % topic_aliases)

            if len(topic_aliases) > 0 and (self.keyword in topic_aliases):
                topic_url = 'https://www.zhihu.com/topic/%s/hot' % topic_id
            else:    
                topic_name = topic_data['object']['name'].lower()
                topic_name = topic_name.replace("<em>", "")
                topic_name = topic_name.replace("</em>", "")
    
                print("topic_name: %s, keyword: %s" % (topic_name, self.keyword))   
                if (topic_name == self.keyword.lower()):
                    # <em>ab</em>血型
                    # print("topic_name: %s, keyword: %s" % (topic_name, self.keyword))
                    topic_url = 'https://www.zhihu.com/topic/%s/hot' % topic_id
                else: 
                    topic_name = topic_name[topic_name.find("（")+1:topic_name.find("）")] if topic_name.find("（") != -1 else topic_name
                    print("English topic_name: %s, keyword: %s" % (topic_name, self.keyword))
                    if (topic_name == self.keyword.lower()):
                    # 伯尔鲁帝（<em>Berluti</em>)
                        topic_url = 'https://www.zhihu.com/topic/%s/hot' % topic_id
        else:
            print(json_data)    
        return topic_url

def do_login(account, password):

    account = ZhihuAccount(account, password)
    account.login(captcha_lang='en', load_cookies=True)   
    account.check_login()        

if __name__ == '__main__':
    do_login('Your ZhiHu Account', 'Password')
    keyword = input('输入搜索的关键词:')
    zhihu = Topic(keyword)
    topic_url = zhihu.get_topic_url()
    print(topic_url)
