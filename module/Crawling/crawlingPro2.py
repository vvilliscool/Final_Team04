from pyspark.sql import SparkSession
from pyspark.sql.types import *

def saveCrawlSave():
    devColumns = [
        StructField("total_id", IntegerType()),
        StructField("s_id", IntegerType()),
        StructField("s_name", StringType()),
    ]
    devSchema = StructType(devColumns)

    csv_text = spark.read.schema(devSchema).option("header", "true").csv("/id_pr/mix_id_all")

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

    csv_text.createOrReplaceTempView('csv')
    df.createOrReplaceTempView('df')

    df2 = spark.sql("select csv.s_id as id, df.s_name, df.s_tel, df.s_photo, df.s_hour, df.s_etc, df.s_menu, df.s_price from df left outer join csv on df.id = csv.total_id").dropna(subset='s_name')
    df2 = df2.dropna(subset='id').orderBy(["id"])

    save_local  = f'/crawling/id_mix/total'
    df2.coalesce(1).write.format("json").mode("overwrite").json(save_local)
    print('save total')

    user = "root"
    password = "1234"
    url = "jdbc:mysql://localhost:3306/meok4"
    driver = "com.mysql.cj.jdbc.Driver"
    dbtable = 'rest_detail'

    df2.write.jdbc(url, dbtable, "overwrite", properties={"driver": driver, "user": user, "password": password})

if __name__ == '__main__':
    spark = SparkSession.builder.master('yarn').appName('strProcess').getOrCreate()
    saveCrawlSave()