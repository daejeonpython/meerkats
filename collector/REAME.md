# 질병정보 수집기 작성

| 분석을 위한 OIE WAHIS(World Animal Health Information System)의 주간 발생정보 수집 


---
## 0. 목적
1. 대시보드 서비스를 위한 기초데이터 수집
2. 인공지능을 활용한 질병 예측모델을 위한 훈련/평가 데이터 목적
---

## 1. 데이터 수집방법
| OIE WAHIS 소개 영상

[![OIE WAHIS]( https://img.youtube.com/vi/kWV64ke6A18/0.jpg)](https://www.youtube.com/embed/kWV64ke6A18) 

1. WAHIS사이트 분석
    - 발생국가, 발생일, 발생지역, 보고일, 발생건수, 발생 질병명 등

![image](https://user-images.githubusercontent.com/53881929/129833411-100c9ae5-8b82-440c-b689-de0e84022d9f.png)

2. 주간발생보고의 데이터 중 분석이 필요한 자료를 선정
| 주간 발생보고(Weekly disease information)는 발생 건이 없는 경우에도 (추이 확인을 위해) 최초 발생이후 1주일 단위로 보고를 실시함. 
| 따라서, 실제로 발생 건이 포함된 보고인지 여부를 확인해야 함

    - susceptible/cases/deaths/killed and Disposed of/slaughtered/killed for commercial use/vaccinated중 하나라도 숫자가 있는 경우에만 발생건으로 간주

    - 군집 발생의 경우 'Number of outbreaks'에 숫자가 있는 경우에 해당 건수를 반영하고, 그렇지 않은 경우에는 1건으로 파악

    - 축종이 여러개이나, 한 건으로 보고된 경우에는 다른 축종은 발생건수를 잡지 않고 NAN으로 둠 (발생건으로 잡으면 발생건수가 데이터와 불일치하는 문제 발생)
    
    - 최초(역학관계가 없는 발생건) 또는 추가(역학적 관련성이 있는 발생건) 인지 확인

![image](https://user-images.githubusercontent.com/53881929/129833993-a6231648-dac6-4e80-8473-9ce2548b5789.png)
![image](https://user-images.githubusercontent.com/53881929/129834030-8c726c61-aa31-445f-a2f1-1bea48d493e0.png)
    


3. 수생동물질병 및 신규 발생정보 없는 데이터 제거
    - 수생 동물 발생건의 경우 조기 리턴으로 처리 (빈 값)

4. Dataframe으로 database에 저장
    - pandas의 DataFrame을 sql에 append 하는 메서드 이용
    - (사전작업) sql table의 컬럼명과 타입을 선 지정해 줌
    - (장점) 모든 컬럼을 한번에 간단히 update가능
    - (단점) 컬럼별로 데이터 타입등을 수정해야 할 때 어려움 있음

6. 영문을 한글로 번역
    - (대상) 국가명, 질병명, 축종명, 구분 등
    
    > 향후 개선방향
    > 한글 컬럼명이 글로벌 서비스에 적합하지 않은 점. 
    > (문제1) DB로 같은 데이터를 2회 쓰는 문제 => 3개의 컬럼에 대해서만 논리를 적용해서 사용할 수 있다는 생각을 못함
    > (해결방안: 단기) 영문으로 작성된 데이터만 API로 제공하고 kibana는 국문으로 번역된 데이터로 운용
    > (해결방안: 장기) 분석팀에서 제시한 distance 논리등을 모듈화 해서 데이터 베이스는 1개로 유지하고, 필요한 컬럼만 모듈을 거쳐 넘기도록 구조 수정


---

## 2. 사용법
1. NewtypeOiescraper.py 파일을 실행

2. 금일 기준 새로운 발생건만 추출
    - 전날까지 데이터베이스의 '리포트 번호'만 추출해서 중복 번호 제거한 리스트를 1개 생성 (1)
    - 최근 발생건 100개의 (1주간) 리포트 번호를 먼저 수집하여 (1)의 리스트와 중복되는 값을 drop
    - 남은 리포트 번호만 순회하면서 금일 데이터를 수집
---
## 3. 주요 기능
1. 매일 오전 1회 WAHIS 데이터 수집
2. elastic search로 데이터 전송
3. 금일 발생건만 필요한 경우 table로 표시(필요시)

---
## 4. 저작권 및 사용권 정보
1. 완전 공개
2. DB관련 접근권한 관리는 '대전파이썬'팀에 문의
---
