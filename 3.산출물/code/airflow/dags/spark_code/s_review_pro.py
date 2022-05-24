#-*- coding: utf-8 -*-
import re
import requests
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace
from functools import reduce
from pyspark.sql.functions import array

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
	"""
	spark = SparkSession.builder.master("yarn").appName("review").getOrCreate()
	## kakao
	# 파일 읽어오기
	s_kakao = spark.read.json("/home/hjyoon/final_data/kakao_pro.json")
	s_kakao.createOrReplaceTempView("s_kakao")
	# s_review (array->str) 바꾸고 s_review null값 제거
	s_kakao = spark.sql("select id,cast(s_review as string) s_review from s_kakao where s_review is not null")
	s_kakao.createOrReplaceTempView("s_kakao")

	# s_review에 []제거
	regex_str = "\[|\]"
	s_kakao = s_kakao.select(col("id"),regexp_replace(col("s_review"), regex_str, "").alias("s_review"))
	s_kakao.createOrReplaceTempView("s_kakao")

	# s_review 전처리
	store = []
	for i in s_kakao.collect():
		# 한글, 숫자, 띄어쓰기, 탭, 줄바꿈, ' 제외-> " " 
		a = re.sub(r"[^0-9가-힣\s\']"," ",i["s_review"])
		a = re.sub("\s+", " ",a)
		a = a.strip()
		store.append((i["id"],a))

	# 전처리 된 값으로 df만들기
	s_kakao = spark.createDataFrame(store,("id","k_review"))
	s_kakao.createOrReplaceTempView("s_kakao")

	# 빈값, None값 없애기
	columns = set(s_kakao.columns) - set(['id'])
	cond = map(lambda x: (col(x).isNotNull()) & (col(x) != ""), columns)
	cond = reduce((lambda x, y: x & y), cond)
	s_kakao = s_kakao.filter(cond)
	s_kakao.createOrReplaceTempView("s_kakao")

	# seoul.csv랑 id 맞추기
	id_file = spark.read.option("header","true").csv("/home/hjyoon/final_data/mix_id.csv")
	id_file.createOrReplaceTempView("id_file")

	s_kakao = spark.sql("select i.s_id, k.k_review k_review from id_file i JOIN s_kakao k ON (i.total_id=k.id)")
	s_kakao.createOrReplaceTempView("s_kakao")

	# 최종 카카오 리뷰데이터 저장
	# s_kakao.write.format("json").mode("overwrite").save("/home/hjyoon/final_data/review/kakao")
	# hdfs dfs -getmerge /home/hjyoon/final_data/review/kakao /home/hjyoon/final_data/kakao_review.json

	## naver
	s_naver = spark.read.json('/home/hjyoon/final_data/naver_pro.json')
	s_naver.createOrReplaceTempView("s_naver")
	s_naver = spark.sql("select id, cast(s_review as string) as s_review from s_naver where s_review is not null")
	s_naver.createOrReplaceTempView("s_naver")

	# s_review에 []제거
	regex_str = "\[|\]"
	s_naver = s_naver.select(col("id"),regexp_replace(col("s_review"), regex_str, " ").alias("s_review"))
	s_naver.createOrReplaceTempView("s_naver")

	store = []
	for i in s_naver.collect():
		a = re.sub(r"[^0-9가-힣\s\']"," ",i["s_review"])
		a = re.sub("\s+", " ",a)
		a = a.strip()
		store.append((i["id"],a))

	s_naver = spark.createDataFrame(store,("id","n_review"))
	s_naver.createOrReplaceTempView("s_naver")

	# 공백 제거
	columns = set(s_naver.columns) - set(['id'])
	cond = map(lambda x: (col(x).isNotNull()) & (col(x) != ""), columns)
	cond = reduce((lambda x, y: x & y), cond)
	s_naver = s_naver.filter(cond)
	s_naver.createOrReplaceTempView("s_naver")

	id_file = spark.read.option("header","true").csv("/home/hjyoon/final_data/mix_id.csv")
	id_file.createOrReplaceTempView("id_file")

	s_naver = spark.sql("select i.s_id, n.n_review n_review from id_file i JOIN s_naver n ON (i.total_id=n.id)")
	s_naver.createOrReplaceTempView("s_naver")

	# s_naver.write.format("json").mode("overwrite").save("/home/hjyoon/final_data/review/naver")
	# hdfs dfs -getmerge /home/hjyoon/final_data/review/naver /home/hjyoon/final_data/naver_review.json

	## dining
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
	# hdfs dfs -getmerge /home/hjyoon/final_data/review/dining /home/hjyoon/final_data/dining_review.json

	## mango
	s_mango = spark.read.option("multiline","True").json("/home/hjyoon/final_data/mango_pro.json")
	s_mango.createOrReplaceTempView("s_mango")
	s_mango = spark.sql("select id,cast(s_review as string) s_review from s_mango where s_review is not null")
	s_mango.createOrReplaceTempView("s_mango")

	regex_str = "\[|\]"
	s_mango = s_mango.select(col("id"),regexp_replace(col("s_review"), regex_str, " ").alias("s_review"))
	s_mango.createOrReplaceTempView("s_mango")

	store = []
	for i in s_mango.collect():
		a = re.sub(r"[^0-9가-힣\s\']"," ",i["s_review"])
		a = re.sub("\s+", " ",a)
		a = re.sub("\n", " ",a)
		a = a.strip()
		store.append((i["id"],a))

	s_mango = spark.createDataFrame(store,("id","m_review"))
	s_mango.createOrReplaceTempView("s_mango")

	columns = set(s_mango.columns) - set(['id'])
	cond = map(lambda x: (col(x).isNotNull()) & (col(x) != ""), columns)
	cond = reduce((lambda x, y: x & y), cond)
	s_mango = s_mango.filter(cond)
	s_mango.createOrReplaceTempView("s_mango")

	# s_mango.write.format("json").mode("overwrite").save("/home/hjyoon/final_data/review/mango")
	# hdfs dfs -getmerge /home/hjyoon/final_data/review/mango /home/hjyoon/final_data/mango_review.json

	## total
	id = spark.range(122759).toDF("id")
	id.createOrReplaceTempView("id")

	tot_review = spark.sql("select distinct(i.id),k.k_review,d.d_review,n.n_review,m.m_review from id i LEFT OUTER JOIN s_kakao k ON (int(k.s_id)=int(i.id)) LEFT OUTER JOIN s_naver n ON (int(i.id) = int(n.s_id)) LEFT OUTER JOIN s_dining d ON (int(i.id) = int(d.s_id)) LEFT OUTER JOIN s_mango m ON (int(i.id) = int(m.id)) order by i.id")
	tot_review.createOrReplaceTempView("tot_review")

	tot_review = tot_review.withColumn("s_review", array(tot_review.k_review, tot_review.n_review, tot_review.d_review, tot_review.m_review))
	tot_review.createOrReplaceTempView("tot_review")
	tot_review = spark.sql("select id,cast(s_review as string) s_review from tot_review")
	tot_review.createOrReplaceTempView("tot_review")
	tot_review = spark.sql("select * from tot_review where s_review<>'[null, null, null, null]'")
	tot_review.createOrReplaceTempView("tot_review")

	# tot_review.write.format("json").mode("overwrite").save("/home/hjyoon/final_data/review/total")

	#  리뷰 테이블 mysql에 넣기
	user="root"
	password="1234"
	url="jdbc:mysql://localhost:3306/mukjalal"
	driver="com.mysql.cj.jdbc.Driver"
	dbtable="s_review"

	tot_review.write.mode("overwrite").option("truncate","true").jdbc(url, dbtable, properties={"driver": driver, "user": user, "password": password})
	"""
	pass
	dbgout(f"s_review SPARK-SUBMIT SUCCESS")
except Exception as ex:
	dbgout(f"s_review SPARK-SUBMIT FAIL -> {str(ex)}")
