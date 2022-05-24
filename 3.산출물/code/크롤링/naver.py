from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import numpy as np
import pandas as pd
import csv
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
seoul = []

with open(dir_path + '/data/api/seoul0.csv') as f:
    seoul_csv = csv.reader(f)
    for sl in seoul_csv:
        seoul.append(sl)

seoul.pop(0)
count = 0

#
for sl in seoul:
    if count == 3: break;
    count += 1
    print(sl)

    s_name = sl[0].replace('(주)','')
    s_add_arr = sl[1].split()
    s_add_gu = s_add_arr[1]
    s_add_dong = s_add_arr[2]
    s_add_ro = ''

    if len(sl[2]) != 0 : s_add_ro = sl[2].split()[2]

    # print('자치구 :',s_add_gu,'\n동 :',s_add_dong)
    # print(s_add_ro)

    l = 0
    for index,s in enumerate(s_add_ro) :
        if str(s).isnumeric() :
            l = index
            break

    s_add_ro = s_add_ro[:l]
    # print(s_add_ro)
    # print()

    service_key = webdriver.chrome.service.Service('../drivers/chromedriver')
    #
    # # try :
    print(count, s_add_gu+" "+s_add_dong+" "+s_name)
    url = f'https://map.naver.com/v5/search/{s_add_gu+"%20"+s_add_dong+"%20"+s_name}/place'
    driver = webdriver.Chrome(service=service_key)
    driver.implicitly_wait(2)
    driver.get(url)  # url 가져오기
    time.sleep(7)
    #
    # 첫번째 아이프레임 찾기 (검색 후 목록)
    search_iframe = driver.find_elements(By.CSS_SELECTOR,'#searchIframe')
    #
    driver.switch_to.frame('searchIframe')  # (2) 특정 프레임으로 전환
    time.sleep(10)
    search_ul = driver.find_elements(By.TAG_NAME,'ul')
    search_li_list = search_ul[0].find_elements(By.TAG_NAME,'li')

    search_li_div = search_li_list[0].find_elements(By.TAG_NAME,'div')
    search_li_div[1].click()

    # 가장 상위의 html로 이동
    driver.switch_to.default_content()
    time.sleep(5)

    search_iframe = driver.find_elements(By.CSS_SELECTOR, '#entryIframe')

    # 두번째 아이프레임 찾기 (가게 클릭 후 아이프레임)
    driver.switch_to.frame('entryIframe')
    time.sleep(5)

    # body = search_iframe.find_element(By.XPATH,'html/body')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    body = soup.find('body',class_='place_on_pcmap')

    search_add = body.find('span',class_='_2yqUQ').get_text()
    search_add_ro = search_add.split('로')[0].split('구')[-1].replace(' ','')+'로'
    print(search_add_ro)
    if search_add_ro == s_add_ro :
        print(search_add_ro,s_add_ro)
    else :
        print(search_add_ro, s_add_ro)
    #
    # driver.close()

#     # except:
#     #     print('에러 발생',s_name)
