from django.shortcuts import render, redirect
from django.utils import timezone
from elasticsearch import Elasticsearch
from django.http import JsonResponse
import requests
import json
from .models import Store, Detail

# Create your views here.
def taste_map(request):
    return render(request, 'store/taste_map.html')


# 홈(Home) 페이지
def theme(request):
        return render(request, 'store/theme.html')


# 검색창(엘라스틱 서치)을 통한 음식점 검색
def ela_store(request):
    if request.method == 'GET':
        q = request.GET['q']
        # query = f'http://localhost:9200/test/_search?q={q}&size=30'
        # ela_data = requests.get(query)
        es = Elasticsearch("http://localhost:9200")
        index = 'store_store'
        body = {
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
    