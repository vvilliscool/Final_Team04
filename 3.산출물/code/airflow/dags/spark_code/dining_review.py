import re
import requests
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace
from functools import reduce

myToken = 'xoxb-3502167542609-3483137286886-0qSsKRxQ9iCkRGd4gHJtCwY4'

def post_message(token, channel, text) :
    response = requests.post('https://slack.com/api/chat.postMessage',
                            headers = {'Authorization' : 'Bearer '+token},
                            data = {'channel' : channel, 'text' : text})
    print(response)

# 오류메세지
def dbgout(message):
    strbuf = datetime.now().strftime('[%m/%d %H:%M:%S] ') + message
    post_message(myToken, '#msg', strbuf)


try:
	spark = SparkSession.builder.master("yarn").appName("dining_review").getOrCreate()

	s_dining = spark.read.json("/home/hjyoon/final_data/dining_pro.json")
	s_dining.createOrReplaceTempView("s_dining")
	s_dining = spark.sql("select id, cast(s_review as string) s_review from s_dining where s_review is not null")
	s_dining.createOrReplaceTempView("s_dining")
	s_dining = spark.sql("select id, cast(s_review as string) s_review from s_dining where s_review <> '[]' and s_review <> '[null]'")
	s_dining.createOrReplaceTempView("s_dining")

	regex_str = "\[|\]"
	s_dining = s_dining.select(col("id"),regexp_replace(col("s_review"), regex_str, " ").alias("s_review"))
	s_dining.createOrReplaceTempView("s_dining")

	store = []
	for i in s_dining.collect():
		a = re.sub(r"[^0-9가-힣\s\']"," ",i["s_review"])
		a = re.sub("\s+", " ",a)
		a = re.sub("\n", " ",a)
		a = a.strip()
		store.append((i["id"],a))

	s_dining = spark.createDataFrame(store,("id","d_review"))
	s_dining.createOrReplaceTempView("s_dining")

	columns = set(s_dining.columns) - set(['id'])
	cond = map(lambda x: (col(x).isNotNull()) & (col(x) != ""), columns)
	cond = reduce((lambda x, y: x & y), cond)
	s_dining = s_dining.filter(cond)
	s_dining.createOrReplaceTempView("s_dining")

	id_file = spark.read.option("header","true").csv("/home/hjyoon/final_data/mix_id.csv")
	id_file.createOrReplaceTempView("id_file")

	s_dining = spark.sql("select i.s_id, d.d_review d_review from id_file i JOIN s_dining d ON (i.total_id=d.id)")
	s_dining.createOrReplaceTempView("s_dining")

	s_dining.write.format("json").mode("overwrite").save("/home/hjyoon/final_data/review/dining")
	dbgout("dining_review SPARK SUBMIT SUCCESS")

except Exception as ex:
	dbgout(f"dining_review SPARK SUBMIT FAIL -> {str(ex)}")
# hdfs dfs -getmerge /home/hjyoon/final_data/review/dining /home/hjyoon/final_data/dining_review.json