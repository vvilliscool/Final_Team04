# kakao map API
# detailed에서 생성한 json파일의 'HSSPLY_ADRES'를 add로 입력
# kakao_location(add)에서 {'lat': 위도, 'lot': 경도, 'b_code': 법정동} 추출
# append_location()으로 json 파일에 위경도, 법정동 코드 항목 추가
import requests
import json

# api => https://developers.kakao.com/product/map
# api 주소, 키
api_keys = ['3ede87edc2f779bef86eca021e732474', '61f8ef2ccb4625e5add4ebc5caa78817']
api_add = 'https://dapi.kakao.com/v2/local/search/address.json'


# kakao API를 이용해 주소의 lot, lat, b_code를 dict의 형태로 retrun
def kakao_location(add):
    # api 설정
    url = api_add# + '?query=' + add
    headers = {"Authorization": f"KakaoAK {api_keys[1]}"}
    query = {'query': add}

    # api result
    result_json = json.loads(str(requests.get(url, headers=headers, params=query).text))

    result_json = dict(result_json)
    # print(result_json)
    # api로 주소의 data를 받았는데 data가 없는 경우
    if len(result_json['documents']) == 0:
        # '충청남도 공주시 금흥동 ....'이라면
        # '공주시 금흥동' 으로 검색하도록
        add1 = add.split(' ')
        qu = f'{add1[0]} {add1[1]} {add1[2]} {add1[3]}'
        query = {'query': qu}
        result_json = json.loads(str(requests.get(url, headers=headers, params=query).text))

    # 위의 두 방법 모두 실패했을 때
    # kakao API로 검색할 수 없는 주소라고 판단하고 좌표값과 법정동코드를 NULL값으로
    if len(result_json['documents']) == 0:
        dict_fail = {'lot': 0.0, 'lat': 0.0}
        return dict_fail

    addr = result_json['documents'][0]['address']

    # 검색이 제대로 된경우 좌표값과 법정동코드 리턴
    result = dict()
    result['lat'] = addr['y']
    result['lot'] = addr['x']

    return result

if __name__ == '__main__':
    # add = '충청남도 공주시 한적2길 51-14'
    # add1 = '공주시 한적2길'
    # # print(add)
    kakao_loca = kakao_location('서울특별시 강남구 대치동 894번지')
    print(kakao_loca)






"""
{
   "documents":[
      {
         "address":{
            "address_name":"서울 강동구 강일동 717",
            "b_code":"1174011000",
            "h_code":"1174051500",
            "main_address_no":"717",
            "mountain_yn":"N",
            "region_1depth_name":"서울",
            "region_2depth_name":"강동구",
            "region_3depth_h_name":"강일동",
            "region_3depth_name":"강일동",
            "sub_address_no":"",
            "x":"127.173182162867",
            "y":"37.5587972921376"
         },
         "address_name":"서울 강동구 고덕로 427",
         "address_type":"ROAD_ADDR",
         "road_address":{
            "address_name":"서울 강동구 고덕로 427",
            "building_name":"고덕리엔파크2단지아파트",
            ...
            "x":"127.173182162867",
            "y":"37.5587972921376",
            "zone_no":"05217"
         },
         "x":"127.173182162867",
         "y":"37.5587972921376"
      }
   ],
   "meta":{
      "is_end":true,
      "pageable_count":1,
      "total_count":1
   }
}

"""