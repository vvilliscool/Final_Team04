from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoAlertPresentException, NoSuchElementException, TimeoutException, ElementNotInteractableException,NoSuchWindowException, NoSuchFrameException, WebDriverException
from bs4 import BeautifulSoup
import requests
from time import sleep
import pandas as pd
import json
from collections import OrderedDict
import datetime


class Mango():

    def __init__(self, file_name):
        self.file_name = file_name

    def crawling(self):
        file_name = self.file_name
        # 음식점 데이터 불러오기
        df = pd.read_csv(f'{file_name}.csv')
        ## id
        s_id = df['id']
        ## 식당 명
        name = df['s_name']
        ## XX구 -> XX으로 바꾸는 작업. ex) 용산구 -> 용산
        ### 서울,경기는 's_add', 's_road' 둘 다 존재하지만 두 컬럼 다 결측치가 존재해서 결측치 처리
        ### 인천은 's_road' 컬럼만 가지고 있어 따로 처리해줬다.
        if 's_add' in df.columns:
            gu_add = df['s_add'].str.split(' ', expand=True)[1].str[:-1].fillna(0)
            gu_road = df['s_road'].str.split(' ', expand=True)[1].str[:-1].fillna(0)
            gu = []
            for i in range(len(df)):
                if gu_road[i] == 0:
                    gu.append(gu_add[i])
                else:
                    gu.append(gu_road[i])
        else:
            df['gu'] = df['s_road'].str.split(' ', expand=True)[1].str[:-1]
            gu = df['gu'].fillna('남')

        ## 도로명 주소(대로)
        road = df['s_road'].str.split(' ', expand=True)[2]


        # 망고플레이트 검색 페이지로 시작
        url = f'https://www.mangoplate.com/search/시작'

        # 다운 받은 webdriver를 가져와
        service = webdriver.chrome.service.Service('chromedriver.exe')
        # 경로를 설정해주고, 브라우저를 자동으로 실행하는 명령을 driver에 저장해준다.
        driver = webdriver.Chrome(service=service)
        # 기다렸다가 url 가져오기
        driver.implicitly_wait(1) 
        driver.get(url)



        # 팝업창 끄기
        ## 프레임으로 이동 
        driver.switch_to.frame(driver.find_element_by_tag_name('iframe'))
        ## 닫기 버튼 누르고
        driver.find_element(By.CSS_SELECTOR, '.ad_btn_wrap:nth-child(2)').click()
        ## 기존 HTML문서로 다시 복귀
        driver.switch_to.default_content()




        # 개수 세기위한 count 정의
        count = 0
        city = []






        # 음식점 데이터 가져와서 그 크기만큼 반복문 실행

        for i in range(len(df)):
            sleep(3)
            # 검색창에 값 입력 후 Enter키
            driver.find_element(By.XPATH, '/html/body/header/div/label/input').send_keys(gu[i] + ' ' + name[i])
            sleep(2)
            driver.find_element(By.XPATH, '/html/body/header/div/label/input').send_keys(Keys.ENTER)
            sleep(2)


            
            # dict 형태 만들기
            store = {}
            


            # 식당이 존재한다면 클릭 시도
            try:
                store['id'] = int(s_id[i])
                # 자꾸 webdriver 어쩌구 대처하기
                try:
                    # 검색 후 처음 나오는 식당을 선택
                    first = driver.find_element(By.XPATH, '/html/body/main/article/div[2]/div/div/section/div[3]/ul/li[1]/div[1]')
                    first.click()
                    sleep(1)
                    
                    print(road[i])
                    print(driver.find_element(By.XPATH, '/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[1]/td').text.split(' ')[2])
                    # 해당 주소가 맞는지 도로명주소의 3번째 요소를 가지고 비교
                    if road[i] == driver.find_element(By.XPATH, '/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[1]/td').text.split(' ')[2]:
                        
                        # 상점명
                        # 만약 지점 데이터가 있다면 상점명 + 지점명
                        if driver.find_element(By.CSS_SELECTOR, '.branch') == NoSuchElementException:
                            store['s_name'] = driver.find_element(By.CSS_SELECTOR, '.restaurant_name').text
                        else:
                            store['s_name'] = (driver.find_element(By.CSS_SELECTOR, '.restaurant_name').text + ' ' + driver.find_element(By.CSS_SELECTOR, '.branch').text).strip()
                            

                        # 주소명
                        ## 지번이 있으면 지번도 가져오기!
                        if driver.find_element(By.XPATH, '/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[1]/td/span[2]') == NoSuchElementException:
                            store['s_road'] = driver.find_element(By.XPATH, '/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[1]/td').text.split('\n')[0]
                        else:
                            store['s_road'] = driver.find_element(By.XPATH, '/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[1]/td').text.split('\n')[0]
                            store['s_add'] = driver.find_element(By.XPATH, '/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[1]/td/span[2]').text
                            
                        
                        
                        ## 상세정보는 주소가 같은 위치에 고정으로 나와있다.
                        ## 그 외의 것들에는 ' 전화번호, 음식 종류, 메뉴, 주차, 영업시간, 쉬는시간, 마지막 주문, 휴일, 웹 사이트 ' 가 있다.
                        
                        # 상세정보 테이블을 가져와서
                        table = driver.find_element(By.CSS_SELECTOR, 'body > main > article > div.column-wrapper > div.column-contents > div > section.restaurant-detail > table > tbody')
                        # tr의 개수를 세준다.
                        tr = table.find_elements_by_tag_name('tr')
                        print(len(tr))
                        # 그리고 5번째부터 tr의 총 개수까지 반복
                        for i in range(2, len(tr)+1):
                            what = driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]')
                            if what == NoSuchElementException:
                                pass
                            else:
                                # 메뉴(문자 형태만)
                                if driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/th').text == '메뉴' and driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/td').text != '' : 
                                    menus = driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/td').text
                                    split_menus = menus.split('\n')
                                    # 메뉴에 사진이 많아서 '+ 숫자'  이런 형태로 될 경우를 제외
                                    if menus[0] != '+':
                                        store['s_menu'] = []
                                        for i in range(0, len(split_menus), 2):
                                            try:
                                                menu = {}
                                                f_name = split_menus[i]
                                                f_price = split_menus[i+1]
                                                menu[f_name] = f_price
                                                store['s_menu'].append(menu)
                                            except IndexError:
                                                pass
                                
                                # 전화번호
                                elif driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/th').text == '전화번호':
                                    store['s_tel'] = driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/td').text
                                # 대표메뉴    
                                elif driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/th').text == '음식 종류':
                                    store['s_repre'] = driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/td').text
                                # 주차
                                elif driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/th').text == '주차':
                                    store['s_parking'] = driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/td').text
                                # 영업시간
                                elif driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/th').text == '영업시간':
                                    store['s_hour'] = driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/td').text
                                # 쉬는시간
                                elif driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/th').text == '쉬는시간':
                                    store['s_break'] = driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/td').text
                                # 마지막주문
                                elif driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/th').text == '마지막주문':
                                    store['s_lastorder'] = driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/td').text
                                # 휴일
                                elif driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/th').text == '휴일':
                                    store['s_holiday'] = driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/td').text
                                # 웹 사이트
                                elif driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/th').text == '웹 사이트':
                                    store['s_link'] = driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/td/a').get_attribute('href')

                        



                        # 리뷰 따오기
                        review_count = int(driver.find_element(By.CLASS_NAME, 'RestaurantReviewList__AllCount').text) 
                        ## 리뷰가 없으면 넘어가기
                        if review_count == 0:
                            pass

                        ## 리뷰가 5개 이하면 바로 리뷰가져오기
                        elif review_count <= 5:
                            print('5개 이하임')
                            print(f'리뷰 개수 : {review_count}')
                            store['s_review'] = []
                            for i in range(1, review_count + 1):
                                review = []
                                re_content = driver.find_element(By.CSS_SELECTOR, f'body > main > article > div.column-wrapper > div.column-contents > div > section.RestaurantReviewList > ul > li:nth-child({i}) > a > div.RestaurantReviewItem__ReviewContent > div > p').text
                                # re_date = driver.find_element(By.CSS_SELECTOR, f'body > main > article > div.column-wrapper > div.column-contents > div > section.RestaurantReviewList > ul > li:nth-child({i}) > a > div.RestaurantReviewItem__ReviewContent > div > span').text
                                
                                # 리뷰 날짜가 'O일 전' 이렇게 나오는 것들 때문에 현재 시간을 구해서 빼줘야함
                                # 'O 시간 전'도 손봐줬음
                                # if '일' in re_date:
                                    # day = int(re_date[0])
                                    # dt_now = datetime.datetime.now()
                                    # current = dt_now.date()
                                    # re_date = str(current - datetime.timedelta(days=day))
                                # elif '시' in re_date:
                                    # hours = int(re_date.split()[0])
                                    # print(hours)
                                    # dt_now = datetime.datetime.now()
                                    # re_date = str((dt_now - datetime.timedelta(hours=hours)).date())
                                # else:
                                    # pass

                                sleep(5)
                                # 날짜와 내용을 list형태로 만들어서 append   
                                # review.append(re_date)
                                # review.append(re_content)
                                store['s_review'].append(re_content)

                        # 그 이상이면 더보기를 일정 횟수 눌러주도록 만들기
                        else:
                            print('5개 이상임')
                            print(f'리뷰 개수 : {review_count}')
                            store['s_review'] = []
                            # 5개마다 더보기가 생긴다. 그리고 한 번당 5개의 리뷰가 또 나온다.
                            for i in range(int(review_count//5)):
                                moreview_button = driver.find_element(By.CLASS_NAME,'RestaurantReviewList__MoreReviewButton')
                                driver.execute_script('arguments[0].click();', moreview_button)
                                sleep(2)
                            for i in range(1, review_count + 1):
                                review = []
                                re_content = driver.find_element(By.CSS_SELECTOR, f'body > main > article > div.column-wrapper > div.column-contents > div > section.RestaurantReviewList > ul > li:nth-child({i}) > a > div.RestaurantReviewItem__ReviewContent > div > p').text
                                # re_date = driver.find_element(By.CSS_SELECTOR, f'body > main > article > div.column-wrapper > div.column-contents > div > section.RestaurantReviewList > ul > li:nth-child({i}) > a > div.RestaurantReviewItem__ReviewContent > div > span').text
                                
                                # 리뷰 날짜가 'O일 전' 이렇게 나오는 것들 때문에 현재 시간을 구해서 빼줘야함
                                # 'O 시간 전'도 손봐줬음
                                # if '일' in re_date:
                                #     day = int(re_date[0])
                                #     dt_now = datetime.datetime.now()
                                #     current = dt_now.date()
                                #     re_date = str(current - datetime.timedelta(days=day))
                                # elif '시' in re_date:
                                #     hours = int(re_date.split()[0])
                                #     print(hours)
                                #     dt_now = datetime.datetime.now()
                                #     re_date = str((dt_now - datetime.timedelta(hours=hours)).date())
                                # else:
                                #     pass

                                sleep(5)
                                # 날짜와 내용을 list형태로 만들어서 append   
                                # review.append(re_date)
                                # review.append(re_content)
                                store['s_review'].append(re_content)

                        # 식당 소개 가져오기
                        if driver.find_element(By.TAG_NAME, 'h3') == NoSuchElementException:
                            pass
                        else:
                            store['s_intro'] = driver.find_element(By.XPATH, '/html/body/main/article/div[1]/div[1]/div/section[2]/div/section/div/p').text


                        city.append(store)
                        count += 1


                    else:
                        city.append(store)
                        count += 1
                        pass


                except WebDriverException as e:
                    # Target Detached
                    sleep(10)
                    # 검색 후 처음 나오는 식당을 선택
                    first = driver.find_element(By.XPATH, '/html/body/main/article/div[2]/div/div/section/div[3]/ul/li[1]/div[1]')
                    first.click()
                    sleep(1)
                    
                    print(road[i])
                    print(driver.find_element(By.XPATH, '/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[1]/td').text.split(' ')[2])
                    # 해당 주소가 맞는지 도로명주소의 3번째 요소를 가지고 비교
                    if road[i] == driver.find_element(By.XPATH, '/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[1]/td').text.split(' ')[2]:
                        
                        # 상점명
                        # 만약 지점 데이터가 있다면 상점명 + 지점명
                        if driver.find_element(By.CSS_SELECTOR, '.branch') == NoSuchElementException:
                            store['s_name'] = driver.find_element(By.CSS_SELECTOR, '.restaurant_name').text
                        else:
                            store['s_name'] = (driver.find_element(By.CSS_SELECTOR, '.restaurant_name').text + ' ' + driver.find_element(By.CSS_SELECTOR, '.branch').text).strip()
                            

                        # 주소명
                        ## 지번이 있으면 지번도 가져오기!
                        if driver.find_element(By.XPATH, '/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[1]/td/span[2]') == NoSuchElementException:
                            store['s_road'] = driver.find_element(By.XPATH, '/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[1]/td').text.split('\n')[0]
                        else:
                            store['s_road'] = driver.find_element(By.XPATH, '/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[1]/td').text.split('\n')[0]
                            store['s_add'] = driver.find_element(By.XPATH, '/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[1]/td/span[2]').text
                            
                        
                        
                        ## 상세정보는 주소가 같은 위치에 고정으로 나와있다.
                        ## 그 외의 것들에는 ' 전화번호, 음식 종류, 메뉴, 주차, 영업시간, 쉬는시간, 마지막 주문, 휴일, 웹 사이트 ' 가 있다.
                        
                        # 상세정보 테이블을 가져와서
                        table = driver.find_element(By.CSS_SELECTOR, 'body > main > article > div.column-wrapper > div.column-contents > div > section.restaurant-detail > table > tbody')
                        # tr의 개수를 세준다.
                        tr = table.find_elements_by_tag_name('tr')
                        print(len(tr))
                        # 그리고 5번째부터 tr의 총 개수까지 반복
                        for i in range(2, len(tr)+1):
                            what = driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]')
                            if what == NoSuchElementException:
                                pass
                            else:
                                # 메뉴(문자 형태만)
                                if driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/th').text == '메뉴' and driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/td').text != '' : 
                                    menus = driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/td').text
                                    split_menus = menus.split('\n')
                                    # 메뉴에 사진이 많아서 '+ 숫자'  이런 형태로 될 경우를 제외
                                    if menus[0] != '+':
                                        store['s_menu'] = []
                                        for i in range(0, len(split_menus), 2):
                                            try:
                                                menu = {}
                                                f_name = split_menus[i]
                                                f_price = split_menus[i+1]
                                                menu[f_name] = f_price
                                                store['s_menu'].append(menu)
                                            except IndexError:
                                                pass
                                
                                # 전화번호
                                elif driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/th').text == '전화번호':
                                    store['s_tel'] = driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/td').text
                                # 대표메뉴    
                                elif driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/th').text == '음식 종류':
                                    store['s_repre'] = driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/td').text
                                # 주차
                                elif driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/th').text == '주차':
                                    store['s_parking'] = driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/td').text
                                # 영업시간
                                elif driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/th').text == '영업시간':
                                    store['s_hour'] = driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/td').text
                                # 쉬는시간
                                elif driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/th').text == '쉬는시간':
                                    store['s_break'] = driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/td').text
                                # 마지막주문
                                elif driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/th').text == '마지막주문':
                                    store['s_lastorder'] = driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/td').text
                                # 휴일
                                elif driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/th').text == '휴일':
                                    store['s_holiday'] = driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/td').text
                                # 웹 사이트
                                elif driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/th').text == '웹 사이트':
                                    store['s_link'] = driver.find_element(By.XPATH, f'/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[{i}]/td/a').get_attribute('href')

                        



                        # 리뷰 따오기
                        review_count = int(driver.find_element(By.CLASS_NAME, 'RestaurantReviewList__AllCount').text) 
                        ## 리뷰가 없으면 넘어가기
                        if review_count == 0:
                            pass

                        ## 리뷰가 5개 이하면 바로 리뷰가져오기
                        elif review_count <= 5:
                            print('5개 이하임')
                            print(f'리뷰 개수 : {review_count}')
                            store['s_review'] = []
                            for i in range(1, review_count + 1):
                                review = []
                                re_content = driver.find_element(By.CSS_SELECTOR, f'body > main > article > div.column-wrapper > div.column-contents > div > section.RestaurantReviewList > ul > li:nth-child({i}) > a > div.RestaurantReviewItem__ReviewContent > div > p').text
                                # re_date = driver.find_element(By.CSS_SELECTOR, f'body > main > article > div.column-wrapper > div.column-contents > div > section.RestaurantReviewList > ul > li:nth-child({i}) > a > div.RestaurantReviewItem__ReviewContent > div > span').text
                                
                                # 리뷰 날짜가 'O일 전' 이렇게 나오는 것들 때문에 현재 시간을 구해서 빼줘야함
                                # 'O 시간 전'도 손봐줬음
                                # if '일' in re_date:
                                    # day = int(re_date[0])
                                    # dt_now = datetime.datetime.now()
                                    # current = dt_now.date()
                                    # re_date = str(current - datetime.timedelta(days=day))
                                # elif '시' in re_date:
                                    # hours = int(re_date.split()[0])
                                    # print(hours)
                                    # dt_now = datetime.datetime.now()
                                    # re_date = str((dt_now - datetime.timedelta(hours=hours)).date())
                                # else:
                                    # pass

                                sleep(5)
                                # 날짜와 내용을 list형태로 만들어서 append   
                                # review.append(re_date)
                                # review.append(re_content)
                                store['s_review'].append(re_content)

                        # 그 이상이면 더보기를 일정 횟수 눌러주도록 만들기
                        else:
                            print('5개 이상임')
                            print(f'리뷰 개수 : {review_count}')
                            store['s_review'] = []
                            # 5개마다 더보기가 생긴다. 그리고 한 번당 5개의 리뷰가 또 나온다.
                            for i in range(int(review_count//5)):
                                moreview_button = driver.find_element(By.CLASS_NAME,'RestaurantReviewList__MoreReviewButton')
                                driver.execute_script('arguments[0].click();', moreview_button)
                                sleep(2)
                            for i in range(1, review_count + 1):
                                review = []
                                re_content = driver.find_element(By.CSS_SELECTOR, f'body > main > article > div.column-wrapper > div.column-contents > div > section.RestaurantReviewList > ul > li:nth-child({i}) > a > div.RestaurantReviewItem__ReviewContent > div > p').text
                                # re_date = driver.find_element(By.CSS_SELECTOR, f'body > main > article > div.column-wrapper > div.column-contents > div > section.RestaurantReviewList > ul > li:nth-child({i}) > a > div.RestaurantReviewItem__ReviewContent > div > span').text
                                
                                # 리뷰 날짜가 'O일 전' 이렇게 나오는 것들 때문에 현재 시간을 구해서 빼줘야함
                                # 'O 시간 전'도 손봐줬음
                                # if '일' in re_date:
                                #     day = int(re_date[0])
                                #     dt_now = datetime.datetime.now()
                                #     current = dt_now.date()
                                #     re_date = str(current - datetime.timedelta(days=day))
                                # elif '시' in re_date:
                                #     hours = int(re_date.split()[0])
                                #     print(hours)
                                #     dt_now = datetime.datetime.now()
                                #     re_date = str((dt_now - datetime.timedelta(hours=hours)).date())
                                # else:
                                #     pass

                                sleep(5)
                                # 날짜와 내용을 list형태로 만들어서 append   
                                # review.append(re_date)
                                # review.append(re_content)
                                store['s_review'].append(re_content)

                        # 식당 소개 가져오기
                        if driver.find_element(By.TAG_NAME, 'h3') == NoSuchElementException:
                            pass
                        else:
                            store['s_intro'] = driver.find_element(By.XPATH, '/html/body/main/article/div[1]/div[1]/div/section[2]/div/section/div/p').text


                        city.append(store)
                        count += 1


                    else:
                        city.append(store)
                        count += 1
                        pass
                
                    

                



                


            except NoSuchElementException:
                count += 1
                city.append(store)
                pass
            
            # 상점마다 파일 덮어쓰기
            if count % 1 == 0:
                mango = OrderedDict()
                mango['store'] = city
                with open(f'mango_{file_name}.json', 'w', encoding='utf-8') as f:
                    json.dump(mango, f, ensure_ascii=False, indent = "\t")

    
seoul = Mango('seoul')
gyeonggi = Mango('gyeonggi')
incheon = Mango('incheon')

seoul.crawling()
# gyeonggi.crawling()
# incheon.crawling()



