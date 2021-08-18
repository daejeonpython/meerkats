# 이미지 수집기 작성

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
3. 주간발생정보의 데이터 중 분석이 필요한 자료를 선정
  - 발생국가, 발생일, 발생지역, 보고일, 발생건수, 발생 질병명 등
4. 수생동물질병 및 신규 발생정보 없는 데이터 제거
5. Dataframe으로 database에 저장
6. 영문을 한글로 번역
---
## 2. 사용법
1. NewtypeOiescraper.py 파일을 실행
2. 금일 기준 새로운 발생건만 추출

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
