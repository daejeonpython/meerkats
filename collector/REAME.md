# 이미지 수집기 작성

| 분석을 위한 OIE WAHIS(World Animal Health Information System)의 주간 발생정보 수집 

<img width="70%" src = 'https://user-images.githubusercontent.com/53881929/128859176-0c891484-50bb-477f-941f-5c0649b05aac.gif'/>

---
## 0. 목적
1. 대시보드 서비스를 위한 기초데이터 수집
2. 인공지능을 활용한 질병 예측모델을 위한 훈련/평가 데이터 목적
---

## 1. 데이터 수집방법
1. WAHIS사이트 분석
2. 주간발생정보의 데이터 중 분석이 필요한 자료를 선정
  - 발생국가, 발생일, 발생지역, 보고일, 발생건수, 발생 질병명 등
3. 수생동물질병 및 신규 발생정보 없는 데이터 제거
4. Dataframe으로 database에 저장
5. 영문을 한글로 번역
---
## 2. 사용법
1. NewtypeOiescraper.py 파일을 실행
2. 금일 기준 새로운 발생건만 추출

---
