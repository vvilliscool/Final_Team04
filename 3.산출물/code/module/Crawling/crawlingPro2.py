from pyspark.sql import SparkSession
from pyspark.sql.types import *

def saveCrawlSave():
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

    load_local = f'/crawling/drop/total/part-0000*'
    df = spark.read.schema(devSchema).json(load_local).dropna(subset='s_name')

    df2 = df.dropna(subset='id').orderBy(["id"])

    user = "root"
    password = "1234"
    url = "jdbc:mysql://localhost:3306/meok4"
    driver = "com.mysql.cj.jdbc.Driver"
    dbtable = 'store_detail'

    df2.write.jdbc(url, dbtable, "overwrite", properties={"driver": driver, "user": user, "password": password})

if __name__ == '__main__':
    spark = SparkSession.builder.master('yarn').appName('strProcess').getOrCreate()
    saveCrawlSave()