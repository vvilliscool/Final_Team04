import json
import requests

# location = './'
location = '/home/ubuntu/git/Final_Team04/data/apiSeoul/'
key = '754542594e6d6a6a34334368754b4b'

# 총 개수와 응답받은 json key이름 반환
def getCountList():
    url = f'http://openapi.seoul.go.kr:8088/{key}/json/LOCALDATA_072404/1/1/'

    response = requests.get(url)
    count_check = json.loads(response.text)
    res_keys = list(count_check.keys())         # LOCALDATA_072404
    loc_keys = list(count_check[res_keys[0]])   # list_total_count, RESULT, row
    total_count = count_check[res_keys[0]][loc_keys[0]]
    print(total_count)
    count_list = list(range(0, total_count, 1000))
    count_list.append(total_count)

    api_dict = dict()
    api_dict['res_keys'] = res_keys
    api_dict['loc_keys'] = loc_keys
    api_dict['count_list'] = count_list

    return api_dict


# 파일 생성
def createFile(api_dict):
    dict_keys = list(api_dict.keys())         # res_keys, loc_keys, count_list

    seoul_list = list()
    cnt = 0

    for i in range(1, len(api_dict[dict_keys[2]])):
        pre, end = api_dict[dict_keys[2]][i-1]+1, api_dict[dict_keys[2]][i]
        url = f'http://openapi.seoul.go.kr:8088/{key}/json/LOCALDATA_072404/{pre}/{end}/'
        response = requests.get(url)

        json_file = json.loads(response.text)
        row_list = json_file[api_dict[dict_keys[0]][0]][api_dict[dict_keys[1]][2]]

        seoul_list = seoul_list + row_list
        print(pre, end)

        if i % 100 == 0 or i == 476:
            # result = dict()
            # result['seoul'] = seoul_list

            with open((location + 'api_seoul'+str(cnt)+'.json'), 'w', encoding='utf8') as file:
                json.dump(seoul_list, file, ensure_ascii=False)

            cnt += 1
            seoul_list = list()


if __name__ == '__main__':
    api_dict = getCountList()
    # for i in range(1, len(api_dict['count_list'])):
    #     if i%100 == 0 or i == 476:
    #         print(i)

    # createFile(api_dict)