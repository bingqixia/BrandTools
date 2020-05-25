# -*- coding: utf-8 -*-
import pandas as pd
import os
import sys
import zhihutopic
import time

class BrandSheet(object):
    def __init__(self, file_path, sheet_name, brand_col='品牌', zhihu_col='知乎'):
        self.file_path = file_path
        self.sheet_name = sheet_name
        self.brand_col = brand_col
        self.zhihu_col = zhihu_col
        self.sheet = self.__read_sheet()

    def __read_sheet(self):
        if not os.path.exists(self.file_path):
            print('[error]: Excel file not found.')
            return
        sheet = pd.read_excel(self.file_path, self.sheet_name, header=0)
        if self.brand_col not in sheet.columns:
            sheet = pd.read_excel(self.file_path, self.sheet_name, header=1)   
        return sheet

    def save_zhihu_topic(self):
        if self.brand_col not in self.sheet.columns:
            print('Brand columns not found.') 
            return
        brand_list = self.sheet[self.brand_col]
        links = []
        for brand in brand_list:
            brand = brand.lower()
            brand = brand[:brand.find('（')] if brand.find('（') != -1 else brand
            brand_search = brand[:brand.find('/')] if brand.find('/') != -1 else brand
            print('品牌名：%s' % brand_search)
            topic = zhihutopic.Topic(brand_search)
            topic_url = topic.get_topic_url()
            if (topic_url == '') and (brand.find('/') != -1):
                brand_search = brand[brand.find('/')+1:]
                topic = zhihutopic.Topic(brand_search)
                topic_url = topic.get_topic_url()
            print('topic_url: %s\n' % topic_url)    
            links.append(topic_url)
        self.sheet[self.zhihu_col] = links
        self.sheet.to_excel(self.file_path, self.sheet_name, index=False) 

def help():
    print('python sheet.py [file_path] [sheet_name]')

def get_account():
    account_info = './account_info'
    if not os.path.exists(account_info):
        account = input('Your ZhiHu Account: ')
        password = input('Password: ')
        with open(account_info, 'w') as f:
            f.write('%s\n%s' % (account, password))
        print('Save account info in account_info.')
        return [account, password]
    else:
        with open(account_info, 'r') as f:
            return f.readlines() 
                  
if __name__ == "__main__":
    if len(sys.argv) != 3:
        help()
        exit()
    account_info = get_account()   
    zhihutopic.do_login(account_info[0], account_info[1])   
    file_path = sys.argv[1]
    sheet_name = sys.argv[2]
    brand_sheet = BrandSheet(file_path, sheet_name)
    brand_sheet.save_zhihu_topic()



