import pyximport
pyximport.install(reload_support=True)
from pyproj import Proj, transform

from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, udf
from pyspark.sql.types import FloatType
from pyspark.sql.functions import when
# from pyspark import SparkContext

# sc = SparkContext('yarn', 'getLocation')
# sc.addFile('/home/big/test_code/getLocKakao.py')
# sc.addFile('/home/big/.local/lib/python3.7/site-packages/pyproj/transformer.py')
spark = SparkSession.builder.master('yarn').appName('getLocation').getOrCreate()
# Tm좌표계 epsg:2097을 위경도 epsg:4326으로 변경해주는 함수
# def tmTrans(x, y):
#     transformer = Transformer.from_crs("epsg:2097", "epsg:4326")
#     converted = transformer.transform(y, x)
#
#     converted = list(converted)
#     converted[0] = round(converted[0] - 0.00005, 6)     # 함수로 변환후 위치값 세부조정한 후
#     converted[1] = round(converted[1] + 0.00285, 6)     # 소수점 7번째 자리에서 반올림
#
#     return converted
def tmTrans(x, y):
    epsg2097 = Proj(init='epsg:2097')
    wgs84 = Proj(init='epsg:4326')
    lot, lat = transform(epsg2097, wgs84, x, y)
    lat = round(lat - 0.00007, 6)
    lot = round(lot + 0.00285, 6)
    result = [lat, lot]
    return result


# kakao API를 이용해 주소의 lot, lat, b_code를 dict의 형태로 retrun
def kakao_location(add):
    api_keys = ['3ede87edc2f779bef86eca021e732474', '61f8ef2ccb4625e5add4ebc5caa78817']
    api_add = 'https://dapi.kakao.com/v2/local/search/address.json'
    # api 설정
    url = api_add# + '?query=' + add
    headers = {"Authorization": f"KakaoAK {api_keys[1]}"}
    query = {'query': add}

    # api result
    result_json = json.loads(str(requests.get(url, headers=headers, params=query).text))

    result_json = dict(result_json)
    # print(result_json)
    # api로 주소의 data를 받았는데 data가 없는 경우
    if len(result_json['documents']) == 0:
        # '충청남도 공주시 금흥동 ....'이라면
        # '공주시 금흥동' 으로 검색하도록
        add1 = add.split(' ')
        qu = f'{add1[0]} {add1[1]} {add1[2]} {add1[3]}'
        query = {'query': qu}
        result_json = json.loads(str(requests.get(url, headers=headers, params=query).text))

    # 위의 두 방법 모두 실패했을 때
    # kakao API로 검색할 수 없는 주소라고 판단하고 좌표값과 법정동코드를 NULL값으로
    if len(result_json['documents']) == 0:
        dict_fail = {'lot': 0.0, 'lat': 0.0}
        return dict_fail

    addr = result_json['documents'][0]['address']

    # 검색이 제대로 된경우 좌표값과 법정동코드 리턴
    result = dict()
    result['lat'] = addr['y']
    result['lot'] = addr['x']

    return result


def trans(x, y, add, loc):
    # loc 위경도 구분 0(lat) / 1(lot)
    if loc > 1:
        print('잘못된 값')
        return 0.0
    # lat인 경우
    if loc == 0:
        # x의 값이 있다면
        if x != None:
            converted= tmTrans(x, y)
            return converted[0]
        else:
            result = kakao_location(add)    # 주소(add)로 좌표 구하는 함수
            return result['lat']
    # lot인 경우
    elif loc == 1:
        # y의 값이 있다면
        if y != None:
            converted = tmTrans(x, y)
            return converted[1]
        else:
            result = kakao_location(add)    # 주소(add)로 좌표 구하는 함수
            return result['lot']
    return 0.0                                # 중간에 if문에 걸리지 않는다면 0


def addCoordinate(df, chk):
    # 위에 정의한 trans함수를 UserDefineFunction으로 정의 return값은 FloatType
    trans_udf = udf(trans, FloatType())

    if chk == 0:
        # 서울 데이터는 lat, lot이 없음으로 X,Y의 값으로 좌표 추가
        df2 = df.withColumn('lat', trans_udf(df.X, df.Y, df.s_add, lit(0))).\
            withColumn('lot', trans_udf(df.X, df.Y, df.s_add, lit(1)))
        return df2
    elif chk == 1:
        # 경기 데이터는 lat, lot이 있음으로 좌표가 비어있는 경우 값 추가
        df2 = df.withColumn('lat', when(df.lat.isNull(), trans_udf(None, None, df.s_add, lit(0)))). \
            withColumn('lot', when(df.lot.isNull(), trans_udf(None, None, df.s_add, lit(1))))
        return df2


def getCoorDf(loca):
    chk = -1
    if loca == 'Seoul':
        chk = 0
    elif loca == 'Gyeonggi':
        chk = 1
    else:
        print("Wrong value. Please enter 'Seoul' or 'Gyeonggi'")

    load_loca = f'/data/toCsv/{loca}/'
    df_data = spark.read.option("header", "true").csv(load_loca + "part-00000*")

    df_data = addCoordinate(df_data, chk)  # lat, lot이 없는 경우 추가
    print(f'Success {loca} Total')

    save_loca = f'/data/addCoordinate/{loca}/'
    df_data.coalesce(1).write.format("com.databricks.spark.csv").mode("overwrite").option("header", "true"). \
        option("encoding", "UTF8").save(save_loca)
    print(f'Success {loca} Save')

if __name__ == '__main__':
    json_names = ['Seoul', 'Gyeonggi']
    for name in json_names:
        getCoorDf(name)