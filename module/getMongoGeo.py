from pymongo import MongoClient, GEOSPHERE
from bson import SON
from pyspark.sql.types import *
from pyspark.sql import SparkSession

import json
import pandas as pd

def getRoundRest(lat, lot):
    client = MongoClient('localhost', 27017)
    db = client['test']
    rest_mongo = db['rest']

    rest_mongo.create_index([("location", GEOSPHERE)])

    rest_loca = rest_mongo.find(
        {'location': {
            '$near': SON([('$geometry',
                           SON([('type', 'Point'),
                                ('coordinates', [float(lot), float(lat)])])),
                          ('$maxDistance', 1000)])}
        })

    row_list = list()
    for row in rest_loca:
        row_dict = {'id': row['id']}
        row_list.append(row_dict)

    return row_list


def getGeoData(row_list):
    row_id = spark.createDataFrame(row_list)

    devColumns = [
        StructField("id", IntegerType()),
        StructField("s_name", StringType()),
        StructField("s_add", StringType()),
        StructField("s_road", StringType()),
        StructField("s_kind", StringType()),
        StructField("lat", FloatType()),
        StructField("lot", FloatType()),
        StructField("s_status", StringType()),
    ]
    devSchema = StructType(devColumns)

    load_loca = f"/data/devSchema/Incheon/"
    df = spark.read.schema(devSchema).option("header", "true").csv(load_loca + "part-00000*")

    df.createOrReplaceTempView('df')
    row_id.createOrReplaceTempView('row_id')

    query = 'select * from df where id in (select id from row_id)'

    df2 = spark.sql(query)




if __name__ == '__main__':
    spark = SparkSession.builder.master('local[1]').appName('mongo').getOrCreate()
    getRoundRest(37.469348, 126.655824)