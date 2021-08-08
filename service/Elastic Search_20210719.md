## Elastic Search

#### 2020-07-19

##### JAVA 8 이상 버젼 필요

```
java -version
```

```
curl -L -O https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.4.3.tar.gz

tar -xvf elasticsearch-5.4.3.tar.gz

cd elasticsearch-5.4.3/bin
```

##### Node시작

```
./elasticsearch
```

`HTTP 주소(192.168.8.112) Port:9200`

http://localhost:9200

http://127.0.0.1:9200

##### Cluster 상태확인

- Cluster 상태 확인을 위해 _cat API 사용

```
GET /_cat/health?v
```

```
http://localhost:9200/_cat/health?v
```

```
Response

epoch      timestamp cluster       status node.total node.data shards pri relo init unassign pending_tasks max_task_wait_time active_shards_percent
1626706383 23:53:03  elasticsearch green           1         1      0   0    0    0        0             0                  -                100.0%


```

- Node 상태확인

```
GET /_cat/nodes?v
```

- 모든 색인 나열

```
GET /_cat/indices?v
```



##### 색인 생성

첫번쨰 명령어로 customer라는 Index 생성

PrettyPrint로 보기위하여 변수로 pretty 입력 

```
PUT /customer?pretty
GET /_cat/indices?v
```

```
Response

health status index    uuid                   pri rep docs.count docs.deleted store.size pri.store.size
yellow open   customer 95SQ4TSUT7mWBT7VNHH67A   5   1          0            0       260b           260b

```

**샤드, 리플리카 개념 배울것!!

customer 인덱스에 추가할때, 유형을 선택해야 한다.

index : customer

type : external

ID : 1

```
PUT /customer/external/1?pretty
{
  "name": "John Doe"
}
```

만든 문서 확인

```
GET /customer/external/1?pretty
```

```
Response
{
  "_index" : "customer",
  "_type" : "external",
  "_id" : "1",
  "_version" : 1,
  "found" : true,
  "_source" : { "name": "John Doe" }
}
```

여기서 found는 요청된 ID 1을 찾았음을 의미한다

#### 요약

```
PUT /customer
PUT /customer/external/1
{
  "name": "John Doe"
}
GET /customer/external/1
DELETE /customer
```

---

---

#### 2021-07-20

accounts.json 을 elasticsearch폴더에 다운로드 후 명령어 실행

```
SampleData Load
https://www.elastic.co/guide/kr/kibana/current/tutorial-load-dataset.html
```



```
curl -H "Content-Type: application/json" -XPOST 'localhost:9200/bank/account/_bulk?pretty&refresh' --data-binary "@accounts.json"
curl 'localhost:9200/_cat/indices?v'
```

```
Response
health status index    uuid                   pri rep docs.count docs.deleted store.size pri.store.size
yellow open   customer QYXsIrmeQ6yP0BnDXtDHjw   5   1          1            0      3.9kb          3.9kb
yellow open   bank     33agckZ4TJ-HjEyDY0X5WA   5   1       1000            0    648.5kb        648.5kb

```

가장 아래에 bank로 indexing된 document 1000개를 확인할 수 있다.

#### 검색 API

```
GET /bank/_search?q=*&sort=account_number:asc&pretty
```

- bank index에서 검색
- q=* 매개변수, account_number 필드를 오름차순으로 결과 정렬

```
Respons Example

{
  "took" : 63,
  "timed_out" : false,
  "_shards" : {
    "total" : 5,
    "successful" : 5,
    "failed" : 0
  },
  "hits" : {
    "total" : 1000,
    "max_score" : null,
    "hits" : [ {
      "_index" : "bank",
      "_type" : "account",
      "_id" : "0",
      "sort": [0],
      "_score" : null,
      "_source" : {"account_number":0,"balance":16623,"firstname":"Bradshaw","lastname":"Mckenzie","age":29,"gender":"F","address":"244 Columbus Place","employer":"Euron","email":"bradshawmckenzie@euron.com","city":"Hobucken","state":"CO"}
    }, {
      "_index" : "bank",
      "_type" : "account",
      "_id" : "1",
      "sort": [1],
      "_score" : null,
      "_source" : {"account_number":1,"balance":39225,"firstname":"Amber","lastname":"Duke","age":32,"gender":"M","address":"880 Holmes Lane","employer":"Pyrami","email":"amberduke@pyrami.com","city":"Brogan","state":"IL"}
    }, ...
    ]
  }
}
```

같은내용을 body에 넣어서 보낼때 쿼리

```
Get /bank/_search
{
	"query": { "match_all":{} },
	"sort":[
		{ "account_number":"asc"}	
	]
}
```



```
took – Elasticsearch가 검색을 실행하는 데 걸린 시간(밀리초)
timed_out – 검색의 시간 초과 여부
_shards – 검색한 샤드 수 및 검색에 성공/실패한 샤드 수
hits – 검색 결과
hits.total – 검색 조건과 일치하는 문서의 총 개수
hits.hits – 검색 결과의 실제 배열(기본 설정은 처음 10개 문서)
hits.sort - 결과의 정렬 키(점수 기준 정렬일 경우 표시되지 않음)
hits._score 및 max_score - 지금은 이 필드를 무시하십시오.
```

### 쿼리소개

https://www.elastic.co/guide/kr/elasticsearch/reference/current/exploring-data.html



RDB랑 쿼리 형식자체는 크게 다르지 않음.

REST API를 이용하여 쿼리를 날린다는 점이 독특함. 

- 테이블이나 Join 개념이 있는지는 확인 필요함
- Json으로 밀어넣은 데이터들이 어디에 보관되어 있는지? 로컬파일?



