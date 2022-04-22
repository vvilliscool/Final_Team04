from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import csv
import os
import json
from selenium.webdriver.common.keys import Keys

dir_path = os.path.dirname(os.path.realpath(__file__))
seoul = [] # 124,500
incheon = [] # 16,384
gyeonggi = [] # 139,481
naver_list = []

# 딕셔너리 덮어쓰기 위한 함수
def toJson(naver_list,name):
    with open(f'naver_{name}.json', 'w', encoding='utf-8') as file :
        json.dump(naver_list, file, ensure_ascii=False, indent='\t')

with open(dir_path + '/data/api/seoul_total_id.csv') as f:
    seoul_csv = csv.reader(f)
    for sl in seoul_csv: seoul.append(sl)
seoul.pop(0)

with open(dir_path + '/data/api/incheon_total.csv') as f :
    incheon_csv = csv.reader(f)
    for ic in incheon_csv : incheon.append(ic)
incheon.pop(0)

with open(dir_path + '/data/api/gyeonggi_total.csv') as f :
    gyeonggi_csv = csv.reader(f)
    for gg in gyeonggi_csv : gyeonggi.append(gg)
gyeonggi.pop(0)


def s_info_seoul_gyeonggi(sl):
    id = sl[0]
    s_name = sl[1].replace('(주)', '')
    s_add_arr = []
    if len(sl[2]) != 0 | len(sl[2].split()) > 3:
        s_add_arr = sl[2].split()
        s_add_gu = s_add_arr[1]
        s_add_dong = s_add_arr[2]
    else:
        s_add_gu, s_add_dong = '', ''
    s_add_ro = ''
    if len(sl[3].strip()) != 0: s_add_ro = sl[3].split()[2].replace(' ', '')

    l = 0
    # 도로명 주소에서 숫자빼고 한글만 가져오기
    for index, s in enumerate(s_add_ro):
        if str(s).isnumeric():
            l = index
            s_add_ro = s_add_ro[:l]
            break
        else:
            pass

    return id,s_name, s_add_arr, s_add_gu, s_add_dong, s_add_ro
def s_info_incheon():
    id = ic[0]
    s_name = ic[1]

    # 인천은 모두 도로명주소 => 동(s_add_dong)이 없음
    # 아예 없는 경우를 대비하여 변수 미리 설정
    s_add_arr = []
    s_add_gu = ''
    s_add_ro = ''

    if len(ic[2]) != 0 | len(ic[2].split()) > 3:
        s_add_arr = ic[2].split()
        s_add_gu = s_add_arr[1]
        s_add_ro = s_add_arr[2].replace(' ', '')

    l = 0
    # 도로명 주소에서 숫자빼고 한글만 가져오기
    for index, s in enumerate(s_add_ro):
        if str(s).isnumeric():
            l = index
            s_add_ro = s_add_ro[:l]
            break
        else:
            pass

    return id,s_name,s_add_arr,s_add_gu,s_add_ro,s_add_ro
def driver_get():
    service_key = webdriver.chrome.service.Service('../drivers/chromedriver')
    url = f'https://map.naver.com/v5/search/서울/place'
    driver = webdriver.Chrome(service=service_key)
    driver.implicitly_wait(2)
    driver.get(url)  # url 가져오기
    time.sleep(7)
    return driver

def s_info_get(naver_dict):
    driver.switch_to.default_content()
    driver.switch_to.frame('entryIframe')
    time.sleep(2)

    # 영업시간 더보기 클릭
    try:
        driver.find_elements(By.CSS_SELECTOR, '._20Y9l')[0].click()
    except:
        pass

    # 주소 더보기 클릭
    driver.find_element(By.CSS_SELECTOR, '._2yqUQ').click()
    time.sleep(1)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    body = soup.find('body', class_='place_on_pcmap')

    # 가져와야 하는 정보 : 홈 - 모든 ul(전화번호, 주소, 영업시간, 기타 정보) / 메뉴
    ## 홈 - ul - li들 ( 전화번호, 주소, 영업시간, 기타 정보 ) / 리뷰 - 리뷰 / 메뉴 - 메뉴
    ul_home = body.find('ul', class_='_6aUG7')
    time.sleep(1)

    # -----------------------------------------------------------------------
    # a. 가게 이름, 가게 연락처, 사진
    naver_dict['id'] = id
    naver_dict['s_name'] = s_name
    naver_dict['s_tel'] = ul_home.find('span', class_='_3ZA0S').get_text()
    # 사진
    photo_arr = list()
    for pt_idx in range(3): photo_arr.append(
        body.find_all('div', class_='_1ZDCY')[pt_idx].find('div', class_='cb7hz _div')['style'].split('(')[
            -1].split(')')[0].replace('\"', ''))
    naver_dict['s_photo'] = photo_arr
    # -----------------------------------------------------------------------
    # b. 주소 & 영업시간
    ul_home_add_div = ul_home.find_all('div', class_='TDq8t')
    # 주소_도로명
    if ul_home.find('span', class_='_3SYpB').get_text() == '도로명': naver_dict['s_road'] = ul_home.find('div',
                                                                                                      class_='TDq8t').get_text().replace(
        '도로명', '').replace('복사', '')
    # 주소_지번
    if ul_home_add_div[-1].find('span', class_='_3SYpB').get_text() == '지번':
        add_text = naver_dict['s_road'].split()[0] + ' ' + naver_dict['s_road'].split()[1] + ' ' + \
                   ul_home_add_div[-1].get_text().replace('지번', '').replace('복사', '')
        naver_dict['s_add'] = add_text[:add_text.find('우')]

    # 영업시간
    try:
        naver_dict['s_hour'] = body.find('span', class_='_20pEw').get_text()
    except:
        naver_dict['s_hour'] = body.find('div', class_='_2ZP3j').get_text()
    # -----------------------------------------------------------------------
    # c. 편의
    for span in body.find_all('span', class_='place_blind'):
        if span.get_text().replace(' ', '') == '편의': naver_dict[
            's_etc'] = span.find_parent().find_next_sibling().get_text()

    ul_arr = body.find_all('span', class_='_3aXen')
    for i in range(len(ul_arr)):
        if ul_arr[i].get_text() == '메뉴': menu_idx = i
        if ul_arr[i].get_text() == '리뷰': review_idx = i
    # -----------------------------------------------------------------------
    # d. 리뷰
    driver.find_elements(By.CSS_SELECTOR, '._3aXen')[review_idx].click()
    time.sleep(1)
    driver.switch_to.default_content()
    driver.switch_to.frame('entryIframe')
    time.sleep(1)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    body = soup.find('body', class_='place_on_pcmap')

    review_cnt = int(body.find('span', class_='place_section_count').get_text())
    review_arr = list()
    # 더보기 버튼 있을 경우 - 최대 200개만 가져오기로
    if review_cnt > 10:
        if (review_cnt // 10) >= 20:
            for_cnt = 20  # 리뷰가 200개가 넘는다면, 최대 20번 더보기 클릭
        else:
            for_cnt = review_cnt // 10  # 리뷰가 200개가 되지 않는다면, 횟수만큼 더보기 클릭
            if review_cnt % 10 == 0: for_cnt - 1  # ex. 리뷰가 20개라면 1번(20//2 - 1)만 누르도록

        for f_cnt in range(for_cnt):
            time.sleep(1)
            driver.switch_to.default_content()
            driver.switch_to.frame('entryIframe')
            time.sleep(1)
            driver.find_element(By.CSS_SELECTOR, '._3iTUo').click()

        driver.switch_to.default_content()
        driver.switch_to.frame('entryIframe')
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        body = soup.find('body', class_='place_on_pcmap')
        time.sleep(3)
        review_li_arr = body.find_all('li', class_='_3FaRE')
        for j in range(len(review_li_arr)): driver.find_elements(By.CSS_SELECTOR,'.WoYOw')[j].click()

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        body = soup.find('body', class_='place_on_pcmap')
        time.sleep(3)
        review_li_arr = body.find_all('li', class_='_3FaRE')

        for j in range(len(review_li_arr)):
            try:
                review_text = review_li_arr[j].find('span', class_='WoYOw').get_text()
                review_arr.append(review_text)
            except:
                pass

    # 더보기 버튼 없을 경우 (전체 리뷰 10개 이하)
    else:
        review_li_arr = body.find_all('li', class_='_3FaRE')
        for j in range(len(review_li_arr)): driver.find_elements(By.CSS_SELECTOR, '.WoYOw')[j].click()

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        body = soup.find('body', class_='place_on_pcmap')
        time.sleep(3)
        review_li_arr = body.find_all('li', class_='_3FaRE')

        for j in range(len(review_li_arr)):
            driver.find_elements(By.CSS_SELECTOR,'.WoYOw')[j].click()
            review_text = review_li_arr[j].find('span', class_='WoYOw').get_text()
            review_arr.append(review_text)
    naver_dict['s_review'] = review_arr
    # -----------------------------------------------------------------------
    # e. 메뉴
    try:
        # 메뉴 리스트 형태 1번 : 일반적인 메뉴 리스트
        driver.switch_to.default_content()
        driver.switch_to.frame('entryIframe')
        ul_arr = driver.find_elements(By.CSS_SELECTOR, '._3aXen')
        ul_arr[menu_idx].click()
        time.sleep(1)
        driver.switch_to.default_content()
        driver.switch_to.frame('entryIframe')
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        body = soup.find('body', class_='place_on_pcmap')
        menu_li_arr = body.find_all('li', class_='_3j-Cj')

        menu_arr = list()
        for i in range(len(menu_li_arr)):
            menu_dict = dict()
            menu_dict[menu_li_arr[i].find('span', class_='_3yfZ1').get_text()] = menu_li_arr[i].find('div',
                                                                                                     class_='_3qFuX').get_text()
            menu_arr.append(menu_dict)

        # 메뉴 리스트 형태 2번 : 주문형태의 메뉴 리스트
        if len(menu_arr) == 0:
            menu_div_arr = driver.find_elements(By.CLASS_NAME, 'd_menu_list')
            # 메뉴 리스트 개수만큼 클릭 후 더보기 버튼 클릭까지 진행
            for menu_i in range(len(menu_div_arr)):
                menu_div = menu_div_arr[menu_i]
                # 2개는 이미 펼쳐져 있음
                if menu_i >= 2: menu_div.click()

                # 더보기 버튼 클릭
                while True:
                    try:
                        menu_div.find_element(By.CLASS_NAME, 'sc_extend_view').click()
                    except:
                        break

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            body = soup.find('body', class_='place_on_pcmap')
            menu_name_arr = body.find_all('div', class_='tit ellp2')

            for menu_j in range(len(menu_name_arr)):
                menu_dict = dict()
                menu_name = menu_name_arr[menu_j].get_text()
                menu_price = menu_name_arr[menu_j].find_next_siblings('div')[-1].get_text()
                menu_dict[menu_name] = menu_price
                menu_arr.append(menu_dict)

        naver_dict['s_menu'] = menu_arr
    except:
        pass
    return naver_dict

def crwaling(driver,name):
    naver_dict = dict()
    menu_idx, review_idx, diff_cnt = 0, 0, 0
    
    driver.switch_to.default_content()
    # 검색 입력창 찾기
    Search_store = driver.find_element(By.XPATH,
                                       'html/body/app/layout/div[3]/div[2]/shrinkable-layout/div/app-base/search-input-box/div/div/div/input')
    Search_store.click()
    time.sleep(2)

    # 기존 입력 지우기
    Search_store.send_keys(Keys.COMMAND + "a")
    Search_store.send_keys(Keys.DELETE)
    Search_store.clear()

    time.sleep(1)

    # 식당명 입력 후 검색하기
    Search_store.send_keys(s_add_dong + ' ' + s_name)
    time.sleep(0.5)
    Search_store.send_keys(Keys.ENTER)
    time.sleep(2)

    print(id, s_name)

    ## 검색어 입력 후, 목록으로 뜰 경우
    try:
        driver.switch_to.frame('searchIframe')
        time.sleep(3)
        search_ul = driver.find_elements(By.TAG_NAME, 'ul')
        search_li_list = search_ul[0].find_elements(By.TAG_NAME, 'li')

        # 모든 목록에 대하여 하나씩
        for i in range(len(search_li_list)):
            # 가게 선택
            search_li_div = search_li_list[i].find_elements(By.TAG_NAME, 'div')
            search_li_div[1].click()

            # 가장 상위의 html로 이동
            driver.switch_to.default_content()
            time.sleep(1)

            # 두번째 아이프레임 찾기 (가게 클릭 후 아이프레임)
            driver.switch_to.frame('entryIframe')
            time.sleep(2)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            body = soup.find('body', class_='place_on_pcmap')

            search_add = body.find('span', class_='_2yqUQ').get_text()
            search_add_ro = search_add.split()[2]

            l = 0
            # 도로명 주소에서 숫자빼고 한글만 가져오기
            for index, s in enumerate(search_add_ro):
                if str(s).isnumeric():
                    l = index
                    search_add_ro = search_add_ro[:l]
                    break

            ## 목록에서 같은 가게를 찾았을 경우
            if search_add_ro == s_add_ro:
                naver_dict = s_info_get(naver_dict)
                break

            ## 목록에서 가게가 다를 경우 : 도로명 주소가 다름
            else:
                diff_cnt += 1
                if (diff_cnt >= 5) | (diff_cnt == len(search_li_list)):
                    naver_dict['id'] = id
                    break

            ## 목록 내 다음 가게 선택 전 driver 위치 재조정
            driver.switch_to.default_content()
            driver.switch_to.frame('searchIframe')
        print()
        # 다음 음식점 검색 전 driver 위치 재조정 ( 검색용 driver 위치 )
        driver.switch_to.default_content()

    ## 검색어 입력 후, 목록으로 뜨지 않을 경우 ( 바로 가게로 뜨거나 목록 ul이 없는 경우 )
    except:
        # 바로 가게로 뜨는 경우
        try:
            naver_dict = s_info_get(naver_dict)
        # 목록 ul이 없는 경우
        except:
            naver_dict['id'] = id

    # 저장하기
    naver_list.append(naver_dict)
    toJson(naver_list,name)

driver = driver_get()

crwaling_cnt = 0
for sl in seoul[5000:]:
    id, s_name, s_add_arr, s_add_gu, s_add_dong, s_add_ro = s_info_seoul_gyeonggi(sl)
    crwaling(driver,'seoul')
    crwaling_cnt += 1
    if crwaling_cnt % 100 == 0 : driver.refresh()



# for ic in incheon[676:]:
#     id,s_name,s_add_arr,s_add_gu,s_add_dong,s_add_ro = s_info_incheon()
#     crwaling(driver,'incheon')


# for gg in gyeonggi:
#     id,s_name, s_add_arr, s_add_gu, s_add_dong, s_add_ro = s_info_seoul_gyeonggi(gg)
    # crwaling(driver,'gyeonggi')




