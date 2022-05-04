import json
import requests

# location = './'         # 파일 생성 경로
location = '/home/ubuntu/git/Final_Team04/data/'
url = 'https://openapi.gg.go.kr/GENRESTRT'
key = 'ffd16fca90e9413f8cf1b42f3078894f'

# 파일 생성
def createFile():
    params = {'Key': key, 'Type': 'json', 'pIndex': 1, 'pSize': 1}
    response = requests.get(url, params=params)
    json_res = json.loads(response.text)

    # 총 개수
    total_cnt = json_res['GENRESTRT'][0]['head'][0]['list_total_count']
    print(total_cnt)
    seoul_list = list()
    cnt = 0
    end = total_cnt//1000 + 2
    for i in range(1, end):
        params = {'Key': key, 'Type': 'json', 'pIndex': i, 'pSize': 1000}
        response = requests.get(url, params=params)

        json_file = json.loads(response.text)
        row_list = json_file['GENRESTRT'][1]['row']

        seoul_list = seoul_list + row_list

        print(i)
        # 90000개 단위로 저장
        if i % 90 == 0 or i == (end-1):
            with open((location + 'api_gyeonggi'+str(cnt)+'.json'), 'w', encoding='utf8') as file:
                json.dump(seoul_list, file, ensure_ascii=False)

            cnt += 1
            seoul_list = list()


if __name__ == '__main__':
    createFile()