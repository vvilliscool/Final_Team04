from pyspark.sql import SparkSession
import getLocKakao
from pyproj import Proj, transform

from pyspark.sql.functions import lit, udf
from pyspark.sql.types import FloatType
from pyspark.sql.functions import when


# Tm좌표계 epsg:2097을 위경도 epsg:4326으로 변경해주는 함수
def tmTrans(x, y):
    epsg2097 = Proj(init='epsg:2097')
    wgs84 = Proj(init='epsg:4326')
    lot, lat = transform(epsg2097, wgs84, x, y)
    lat = round(lat - 0.00007, 6)
    lot = round(lot + 0.00285, 6)
    result = [lat, lot]
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
            result = getLocKakao.kakao_location(add)    # 주소(add)로 좌표 구하는 함수
            return result['lat']
    # lot인 경우
    elif loc == 1:
        # y의 값이 있다면
        if y != None:
            converted = tmTrans(x, y)
            return converted[1]
        else:
            result = getLocKakao.kakao_location(add)    # 주소(add)로 좌표 구하는 함수
            return result['lot']
    return 0.0                                # 중간에 if문에 걸리지 않는다면 0


def addCoordinate(df, chk):
    df.createOrReplaceTempView('df')

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

if __name__ == '__main__':
    spark = SparkSession.builder.master('yarn').appName('getLocation').getOrCreate()
    print(tmTrans(189814.305918917, 443046.239859063))