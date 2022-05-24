from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark import SparkContext
from pymongo import MongoClient, GEOSPHERE

client = MongoClient('localhost', 27017)
db = client['test']

def makeMongoSet():
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

    load_loca = "/data/total_rest"
    df = spark.read.schema(devSchema).option("header", "true").csv(load_loca + "/part-00000*")
    df.createOrReplaceTempView('df')

    devColumns = [
        StructField("id", IntegerType()),
        StructField("s_name", StringType()),
        StructField("s_tel", StringType()),
        StructField("s_photo", StringType()),
        StructField("s_hour", StringType()),
        StructField("s_etc", StringType()),
        StructField("s_menu", StringType()),
        StructField("s_price", StringType()),
    ]
    devSchema = StructType(devColumns)
    load_loca = "/crawling/drop/total"
    df2 = spark.read.json(load_loca+"/part-0000*", encoding='utf8')
    df2.createOrReplaceTempView('df2')

    sql = 'select df.id, df.s_name, df.s_road, df.s_add, df.s_kind, df.lat, df.lot from df join df2 on df.id=df2.id'
    df_sql = spark.sql(sql)
    df3 = df_sql.collect()

    df_list = list()
    for row in df3:
        df_list2 = list()
        df_list2.append(row['lot'])
        df_list2.append(row['lat'])
        df_dict = {'id': (row['id']), 's_name': row['s_name'], 's_add': row['s_add'], 's_road': row['s_road'],
                   'location': {'type': 'Point', 'coordinates': df_list2}}
        df_list.append(df_dict)
        if row['id'] % 100 == 0:
            print(row['id'])

    rest_mongo = db['detail']
    rest_mongo.drop()
    rest_mongo = db['detail']
    rest_mongo.create_index([("location", GEOSPHERE)])

    rest_mongo.insert_many(df_list)

if __name__ == '__main__':
    spark = SparkSession.builder.master('local[1]').appName('addMongodb').getOrCreate()
    makeMongoSet()