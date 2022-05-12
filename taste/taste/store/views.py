# from django.shortcuts import render, redirect

# Create your views here.
# def taste_map(request):
#     return render(request, 'store/taste_map.html')

# def theme(request):
#     return render(request, 'store/theme.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from elasticsearch import Elasticsearch
from django.http import JsonResponse
import requests
import json

from review.models import Review
from .models import Store, Detail, Weather
from pymongo import MongoClient, GEOSPHERE
from bson import SON
import pandas as pd

# Create your views here.
def taste_map(request):
    return render(request, 'store/taste_map.html')


# 홈(Home) 페이지
def theme(request):
    weather = Weather.objects.filter(id=1)[0]
    
    # 토픽 리스트(0~9)
    topics = pd.read_csv('./static/resources/data/topic_lst.csv', index_col=0)
    topic_id = list(topics['id'])
    topic_theme = list(topics['theme'])
    topic = []
    for i in range(len(topic_id)):
        tmp = {}
        tmp['id'] = topic_id[i]
        tmp['theme'] = topic_theme[i]
        topic.append(tmp)



    context = {
        'weather':weather,
        'topic':topic,
    }
    return render(request, 'store/theme.html', context)



# 테마 선택시 음식점 나오는 페이지
def theme_stores(request, topic_pk):
    topics = pd.read_csv('./static/resources/data/topic_lst.csv', index_col=0)
    topic_theme = list(topics['theme'])
    topic = topic_theme[int(topic_pk)]
    print(topic)

    themes = pd.read_csv('./static/resources/data/theme.csv', index_col=0)
    # 쓸 컬럼(Dominant_Topic, id1(store_id라고 생각하면 된다.), theme)
    theme_stores_id = list(themes[themes['Dominant_Topic'] == int(topic_pk)]['id.1'])
    
    result = list()
    # 다 가져오면 너무 오래걸리므로 30개만 가져오기
    stores = Store.objects.filter(id__in=theme_stores_id)[:30]
    for rest in stores:
        data = {'id': rest.id, 'source':{'s_name':rest.s_name,'s_add':rest.s_add,'s_road':rest.s_road, 's_kind':rest.s_kind}}
        result.append(data)


    # 음식점 세부사항 보내기 
    details = Detail.objects.values('id', 's_photo')
        
    detail = list()
    for obj in details:
        if obj['s_photo'] != None:
            photos = json.loads(obj['s_photo'])
            photo1 = photos['content'][0]
            photo2 = photos['content'][1]
            photo3 = photos['content'][2]
            data = {'id': obj['id'], 'photo1':photo1, 'photo2':photo2, 'photo3':photo3}
            detail.append(data)
    
    context = {
        'topic':topic,
        'result':result,
        'detail':detail,
    }
    return render(request, 'store/theme_stores.html', context)


# 검색창(엘라스틱 서치)을 통한 음식점 검색
def ela_store(request):
    if request.method == 'GET':
        q = request.GET['q']
        # query = f'http://localhost:9200/test/_search?q={q}&size=30'
        # ela_data = requests.get(query)
        es = Elasticsearch("http://localhost:9200")
        index = 'store_store'
        body = {
            "size": 30,
            "query" : {
                "multi_match" : {
                    "fields" : ["s_name", "s_road", "s_add", "s_kind"],
                    "query" : q,
                    "type" : "phrase_prefix"
                }
            }
        }
        res = es.search(index=index, body=body)
        hits_datas = res['hits']['hits']

        # 몽고로 보내고 저장한 후 다시 결과로 뽑아내는..
        # BBQ라고 검색한다면, BBQ와 관련된 모두 가져와서 형태로 가공 후 몽고DB에 올리고
        # 사용자 기반 lat, lot 으로 위치검색 후 가까운 위치 순서대로 return 후
        # HTML에 반영시켜 줌
        # mongo_list = list()
        # for data in hits_datas:
        #     local = list()
        #     local.append(data['_source']['lot'])
        #     local.append(data['_source']['lat'])
        #     hits_data = {'id': data['_id'], 's_name': data['_source']['s_name'], 's_add': data['_source']['s_add'], 's_road': data['_source']['s_road'],
        #            's_kind': data['_source']['s_kind'], 'location': {'type': 'Point', 'coordinates': local}}
        #     mongo_list.append(hits_data)

        # client = MongoClient('localhost', 27017)
        # db = client['test']
        # rest_mongo = db['rest']
        # rest_mongo.drop()
        # rest_mongo = db['rest']
        # rest_mongo.create_index([("location", GEOSPHERE)])
        # rest_mongo.insert_many(mongo_list)

        # # 검색버튼을 눌렀을때 사용자의 lat과 lot 데이터
        # result = getRoundRest(lat, lot, 'rest')

        # 음식점 정보들을 처리하기 쉽게 변경해서 template으로 보냄
        result = list()
        for data in hits_datas:
            hits_data = {'id': data['_id'], 'source': data['_source']}
            result.append(hits_data)




        store = Store.objects.all()
        



        # 상세정보에서 음식점 사진 있는거 3개로 나눠서 보내버리기!
        details = Detail.objects.values('id', 's_photo')
        
        detail = list()
        for obj in details:
            if obj['s_photo'] != None:
                photos = json.loads(obj['s_photo'])
                photo1 = photos['content'][0]
                photo2 = photos['content'][1]
                photo3 = photos['content'][2]
                data = {'id': obj['id'], 'photo1':photo1, 'photo2':photo2, 'photo3':photo3}
                detail.append(data)

        context = {
            'result': result,
            'store': store,
            'detail': detail,
        }

        return render(request, 'store/store_list.html', context)


# 검색창 자동완성 기능
def autocom(request):
    es = Elasticsearch("http://localhost:9200")
    index = 'store_store'

    q = request.GET.get("key")
    if q == None:
        result = {"key": None}
        return result

    body = {
        "query" : {
            "multi_match" : {
                "fields" : ["s_name"],
                "query" : q,
                "type" : "phrase_prefix"
            }
        }
    }
    res = es.search(index=index, body=body)
    hits_datas = res['hits']['hits']

    s_name = list()
    for data in hits_datas:
        hits_data = {'s_name': data['_source']['s_name']}
        s_name.append(hits_data)
    print(s_name)
    result = {"key": s_name}

    return JsonResponse(result)


def autocom2(request):
    es = Elasticsearch("http://localhost:9200")
    index = 'store_store'

    q = request.GET.get("key")
    if q == None:
        result = {"key": None}
        return result

    body = {
        "query" : {
            "multi_match" : {
                "fields" : ["s_name"],
                "query" : q,
                "type" : "phrase_prefix"
            }
        }
    }
    res = es.search(index=index, body=body)
    hits_datas = res['hits']['hits']

    s_name = list()
    for data in hits_datas:
        hits_data = {'s_name': data['_source']['s_name']}
        s_name.append(hits_data)
    print(s_name)
    result = {"key": s_name}

    return JsonResponse(result)

def autocom3(request, topic_pk):
    es = Elasticsearch("http://localhost:9200")
    index = 'store_store'

    q = request.GET.get("key")
    if q == None:
        result = {"key": None}
        return result

    body = {
        "query" : {
            "multi_match" : {
                "fields" : ["s_name"],
                "query" : q,
                "type" : "phrase_prefix"
            }
        }
    }
    res = es.search(index=index, body=body)
    hits_datas = res['hits']['hits']

    s_name = list()
    for data in hits_datas:
        hits_data = {'s_name': data['_source']['s_name']}
        s_name.append(hits_data)
    print(s_name)
    result = {"key": s_name}

    return JsonResponse(result)



def store_detail(request, store_pk):
    store = get_object_or_404(Store, pk=store_pk)
    
    # 상세 정보
    details = Detail.objects.filter(id=store_pk)
    detail = list()
    data = {}
    if len(details) == True:
        obj = details[0]
        data['id'] = obj.id
        if obj.s_photo != None:
            photos = json.loads(obj.s_photo)
            data['photo1'] = photos['content'][0]
            data['photo2'] = photos['content'][1]
            data['photo3'] = photos['content'][2]
        else:
            data['photo1'] = None
            data['photo2'] = None
            data['photo3'] = None
        data['s_tel'] = obj.s_tel
        data['s_hour'] = obj.s_hour
        data['s_etc'] = obj.s_etc
        detail.append(data)

        # 메뉴는 따로
        if obj.s_menu != None:
            menus = json.loads(obj.s_menu)
            prices = json.loads(obj.s_price)
            data['s_menu'] = zip(menus['content'], prices['content'])


    # 리뷰 부분
    reviews = Review.objects.filter(store_id=store_pk).order_by('-pk')

    context = {
        'store': store,
        'detail': detail,
        'reviews':reviews,
    }
    return render(request, 'store/store_detail.html', context)
    





def getRoundRest(lat, lot, db_name):
    client = MongoClient('localhost', 27017)
    db = client['test']
    rest_mongo = db[db_name]

    rest_mongo.create_index([("location", GEOSPHERE)])

    distance = 1000
    stop = 200
    # if db_name == 'detail':
    #     distance = 500


    rest_loca = rest_mongo.find(
        {'location': {
            '$near': SON([('$geometry',
                           SON([('type', 'Point'),
                                ('coordinates', [float(lot), float(lat)])])),
                          ('$maxDistance', distance)])}
        })

    row_list = list()
    cnt = 0
    for row in rest_loca:
        row_dict = {'id': row['id'], 's_name': row['s_name'], 's_add': row['s_add'],
                    'location': row['location']['coordinates'] }
        row_list.append(row_dict)
        if db_name == 'detail' and cnt == stop:
            break
        cnt += 1

    return row_list


def geo_add(request):
    lot = request.GET.get("lot")
    lat = request.GET.get("lat")
    print(lot, lat)
    loca_list = getRoundRest(lat, lot, 'detail')

    print(loca_list)
    
    result = {"key": loca_list}
    return JsonResponse(result)



