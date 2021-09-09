## 분석기

&nbsp;

![2021-09-09_094325](https://user-images.githubusercontent.com/13086891/132606866-9122e073-41bf-42b3-9dba-27d46bca361e.png)

&nbsp;

#### I. 주요 기능

1. 수집된 DB 데이터를 전처리하여 추후 Kibana 대시보드에 전시할 수 있도록 Elasticsearch 인덱스에 삽입
2. DB에서 CRUD(Create, Read, Update, Delete) 연산을 통해 발생하는 변경사항을 ES 인덱스에 반영함으로써 DB와 Elasticsearch 간의 동기화 유지 (개발 예정)
3. 전처리된 데이터를 입력으로 하여 향후 질병 발생 양상을 에측 (개발 예정)

&nbsp;

#### II. 처리 흐름

1. 스케줄러
   - Linux Service를 통해 매일 오전 9시에 분석기 실행
2. 분석기
   1. 분석기는 크게 3가지 프로세스, 즉 '읽기', '예측', '쓰기'로 구성됨
      1. 읽기
         - DB의 모든 row를 읽어들여 쓰기 및 예측에 적합한 형태로 데이터 전처리
      2. 예측 (개발 예정)
         - 전처리된 데이터를 입력으로 하여 현재 시점 t를 기준으로 t+1 내지 t+n까지의 질병 발생 양상 예측
      3. 쓰기
         1. Elasticsearch 인덱스
            - a. DB의 총 46개 column 중 (1) row id, (2) 발생일, (3) 질병, (4) 혈청형, (5) 축종, (6) 구분, (7) 건수, (8) 지역, (9) 국가, (10) 발생 지역, (11) 위경도 column을 인덱싱
            - DB의 row id와 ES의 document id를 1:1 매핑
            - bulk indexing을 통해 인덱스 일괄 업데이트
         2. csv 파일
            - 데이터 공유를 목적으로 DB 데이터를 csv 파일로 출력







