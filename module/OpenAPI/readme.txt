Open API pipe
api_incheon.py, getGyeonggi.py, getSeoul.py로 받은 json(or csv)파일이 Hadoop( '/'[루트경로] )에 저장되어있을 때
pipe1	파일을 불러와 하나의 파일로 만든다
pipe2	s_name, s_add, s_road등 이상치 처리
pipe3	Tm좌표계나 주소로 위경도 columns 생성
pipe4	서울, 경기, 인천 데이터를 하나의 파일로 만들고 MySQL의 Talbe로 저장
pipe5	MongoDB에 데이터 저장