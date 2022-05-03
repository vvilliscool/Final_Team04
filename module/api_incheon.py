import requests
import pandas as pd
import json
import math

serviceKey = "G8%2F6kLlqz2GninZfrl6HupkMdDQuH84vtXL9uJ7Pp8fYP7EhO8JJADYKZCJlTCZd0AbiIy9pCJP%2B151EAPYwRw%3D%3D"
res_lst = []

cnt = 1
i = 0
while True:
    url = f"https://api.odcloud.kr/api/15048906/v1/uddi:76d78696-e2d6-42e2-9a6f-fd855beba945_201909261643?page={cnt}&perPage=1000&serviceKey={serviceKey}"
    resp = requests.get(url)
    resp.encoding = "UTF-8"
    total = int(resp.json()['totalCount'])
    store_lst = resp.json()['data']
    for store in store_lst:
        store_dict = dict()
        store_dict['id'] = i
        if '(주)' not in store['업소명']:
            store_dict['s_name'] = store['업소명']
        else:
            store_dict['s_name'] = store['업소명'][3:]
        store_dict['s_add'] = None
        store_dict['s_road'] = store['업소주소']
        store_dict['s_kind'] = store['업태']
        store_dict['lat'] = None
        store_dict['lot'] = None
        store_dict['s_status'] = store['영업상태']
        res_lst.append(store_dict)
        i += 1
    
    if cnt == math.ceil(total/1000):
        break
    cnt += 1

res_dict = dict()
res_dict = res_lst

# json으로 저장하기
result_json = json.dumps(res_dict, ensure_ascii=False)
with open('incheon_total.json', 'w', encoding='utf-8') as f:
    f.write(result_json)

# json to csv
result_csv = json.loads(result_json)
df = pd.json_normalize(result_csv)
df.to_csv("incheon_total.csv", index=False)