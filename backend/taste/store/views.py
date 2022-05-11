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

# Create your views here.
def taste_map(request):
    return render(request, 'store/taste_map.html')


# 홈(Home) 페이지
def theme(request):
    weather = Weather.objects.filter(id=1)[0]
    context = {
        'weather':weather,
    }
    return render(request, 'store/theme.html', context)


# 검색창(엘라스틱 서치)을 통한 음식점 검색
def ela_store(request):
    if request.method == 'GET':
        q = request.GET['q']
        # query = f'http://localhost:9200/test/_search?q={q}&size=30'
        # ela_data = requests.get(query)
        es = Elasticsearch("http://localhost:9200")
        index = 'store_store'
        body = {
            "size": 50,
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

        # 몽고 버전?
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
    print('처음')
    print(request.path)
    add = request.path.split('/')
    print(add)
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
    print('처음')
    print(request.path)
    add = request.path.split('/')[4]
    print(add)
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
    result = {"key": s_name, 'add':add}

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
    if db_name == 'detail':
        distance = 500


    rest_loca = rest_mongo.find(
        {'location': {
            '$near': SON([('$geometry',
                           SON([('type', 'Point'),
                                ('coordinates', [float(lot), float(lat)])])),
                          ('$maxDistance', 1000)])}
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