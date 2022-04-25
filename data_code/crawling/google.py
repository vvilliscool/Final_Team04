import csv

import requests
from bs4 import BeautifulSoup

import subprocess

from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoAlertPresentException, NoSuchElementException, TimeoutException, ElementNotInteractableException,NoSuchWindowException, NoSuchFrameException, WebDriverException

import pandas as pd
import json 
from collections import OrderedDict
import datetime

class Google():

    def __init__(self, file_name):
        self.file_name = file_name
    

    def crawling(self):
        file_name = self.file_name
        prefix = 'https://www.google.co.kr/maps/search/'
        df = pd.read_csv(f'{file_name}.csv')
        s_id = df['id']
        name = df['s_name']
        if 's_add' in df.columns:
            add = []
            for i in range(len(df)):
                if str(df['s_road'][i]) != 'nan':
                    add.append(df['s_road'][i])
                else:
                    add.append(df['s_add'][i])
        else:
            add = list(df['s_road'])
        
        urls = []
        for i in range(len(df)):
            urls.append(prefix + str(add[i]) + ' ' + str(name[i]))


        city = []
        count = 0 

        for i in range(len(df)):
            try: # "C:\Program Files (x86)\Google\Chrome\Application"
                subprocess.Popen(r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"')

                service = Service('./chromedriver.exe')
                option = Options()
                option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
                option.add_argument("headless")
                browser = webdriver.Chrome(service=service, options=option)
                browser.get(urls[i])
                sleep(2)
                review_num_text = browser.find_element(By.CLASS_NAME, "Yr7JMd-pane-hSRGPd").text
                review_num = int(review_num_text.split(' ')[1][:-1])
                browser.find_element(By.CLASS_NAME, "Yr7JMd-pane-hSRGPd").click()
                print(review_num)
                
                
                store = {}
                print(int(s_id[i]))
                store['id'] = int(s_id[i])
                count += 1
                store['s_review'] = []
                # 여기에 스크롤 크롤링 하는 코드 넣으시면 됩니다.
                sleep(10)
                ## 리뷰가 10개 이하일 때
                
                if review_num <= 10:
                    print('리뷰 10개 이하!')
                    for j in range(review_num):
                        review_content = browser.find_elements(By.CSS_SELECTOR, '.wiI7pd')[j].text
                        store['s_review'].append(review_content)
                
                # 리뷰가 11개 이상일 때
                else:
                    print('리뷰 11개 이상')
                    for k in range(review_num):
                        itemlist = browser.find_element_by_css_selector('.m6QErb.DxyBCb.cYB2Ge-oHo7ed.cYB2Ge-ti6hGc') 
                        browser.execute_script('arguments[0].scrollBy(0,500)', itemlist)
                        sleep(0.5)
                    

                    # if review_num > 100:
                        # for j in range(100):
                            # review_content = browser.find_elements(By.CSS_SELECTOR, '.wiI7pd')[j].text
                            # store['s_review'].append(review_content)
                            # sleep(0.1)
                            # print(f'{review_num} 중 {j}개 완료')                              
                    # else:
                    for j in range(review_num):
                        review_content = browser.find_elements(By.CSS_SELECTOR, '.wiI7pd')[j].text
                        store['s_review'].append(review_content)
                        sleep(0.1)

                try:
                    city.append(store)
                    print('데이터 올라갔다.')
                except Exception as err:
                    city.append(store)
                    print('데이터 올라갔다.')
                


            except Exception as err:
                store = {}
                store['id'] = int(s_id[i])
                count += 1
                store['s_review'] = []
                city.append(store)
                with open(f'errors_{file_name}.txt', 'a', encoding='utf8') as f:
                    f.write(f'{s_id[i]}\n')
            finally:
                browser.close()

            if count % 1 == 0:
                    google = OrderedDict()
                    google['store'] = city
                    with open(f'google_{file_name}.json', 'w', encoding='utf-8') as f:
                        json.dump(google, f, ensure_ascii=False, indent = "\t")


seoul = Google('seoul')
gyeonggi = Google('gyeonggi')
incheon = Google('incheon')

seoul.crawling()
# gyeonggi.crawling()
# incheon.crawling()