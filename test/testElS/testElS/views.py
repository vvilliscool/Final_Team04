from django.shortcuts import render, redirect
from django.utils import timezone
from elasticsearch import Elasticsearch
from django.http import JsonResponse

import requests
import json

from pymongo import MongoClient, GEOSPHERE
from bson import SON
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


def index(request):
    return render(request, 'index.html')


def elaSearch(request):
    if request.method == 'GET':
        q = request.GET['q']
        # query = f'http://localhost:9200/test/_search?q={q}&size=30'
        # ela_data = requests.get(query)
        es = Elasticsearch("http://localhost:9200")
        index = 'inch'
        body = {
            "size": 10000,
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

        mongo_list = list()
        for data in hits_datas:
            local = list()
            local.append(data['_source']['lot'])
            local.append(data['_source']['lat'])
            hits_data = {'id': data['_id'], 's_name': data['_source']['s_name'], 's_add': data['_source']['s_add'], 's_road': data['_source']['s_road'],
                   's_kind': data['_source']['s_kind'], 'location': {'type': 'Point', 'coordinates': local}}
            mongo_list.append(hits_data)

        client = MongoClient('localhost', 27017)
        db = client['test']
        rest_mongo = db['rest']
        rest_mongo.drop()
        rest_mongo = db['rest']
        rest_mongo.create_index([("location", GEOSPHERE)])
        rest_mongo.insert_many(mongo_list)

        # 검색버튼을 눌렀을때 사용자의 lat과 lot 데이터
        result = getRoundRest(lat, lot, 'rest')

        return render(request, 'search.html', {'result': result})

def autocom(request):
    es = Elasticsearch("http://localhost:9200")
    index = 'inch'

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


def taste_map(request):
    return render(request, 'taste_map.html')



def geo_add(request):
    lot = request.GET.get("lot")
    lat = request.GET.get("lat")
    print(lot, lat)
    loca_list = getRoundRest(lat, lot, 'detail')

    print(loca_list)
    
    result = {"key": loca_list}
    return JsonResponse(result)