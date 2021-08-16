import argparse
import json
import pymysql
from elasticsearch.client import Elasticsearch
from elasticsearch import helpers
from temp.edit_distance import disease_convert, species_convert
from temp.kr_dictionary import disease_dict, species_dict

def read_from_db(host, user, password, table, display_rows=False):
    
    print("Reading data from db...")
    reverse_disease_dict = {value: key for (key, value) in disease_dict.items()}
    reverse_species_dict = {value: key for (key, value) in species_dict.items()}

    try:
        conn = pymysql.connect(host=host, user=user, password=password)
        curs = conn.cursor()
        curs.execute("SHOW DATABASES")
        db_info = curs.fetchall()
        print(f'# Database information: {db_info}')

        curs.execute("SHOW TABLES FROM " + user)
        table_info = curs.fetchall()
        print(f'# List of tables of {user}: {table_info}')
        target_table = user + "." + table
        
        curs.execute("SELECT * FROM " + target_table)
        column_info = curs.description
        print("# List of columns:")        
        for idx, col in enumerate(column_info):
            print(idx, col[0])

        curs.execute("SELECT 발생일, 질병, 혈청형, 축종, 구분, 건수, 국가, `발생 지역`, 위경도 FROM " + target_table)
        rows = curs.fetchall()
        # tuple -> list
        rows = [list(x) for x in rows]

        for idx, row in enumerate(rows):
            if row[1] not in reverse_disease_dict:
                row[1] = disease_convert(row[1])
            if row[3] not in reverse_species_dict:
                row[3] = species_convert(row[3])
            if row[8] != None:
                # ex) string: "[26.3, 27.3]" -> float list: [26.3, 27.3]
                row[8] = row[8].lstrip("[").rstrip("]").split(",")
                row[8] = [float(x) for x in row[8]]
            if display_rows:
                print(idx, row)
            
        print(f'# Number of rows: {len(rows)}')
        return rows
    
    except Exception as ex:
        print(ex)


def write_to_elastic(host, mapping_definition, index_name, rows):
    
    print("Writing extracted data into Elasticsearch...")
    es = Elasticsearch(host)
    with open(mapping_definition, "r", encoding="utf-8") as json_file:
        mapping = json.load(json_file)

    if es.indices.exists(index=index_name) is False:
        es.indices.create(index=index_name, body=mapping)
    
    bulk_actions = []
    for idx, row in enumerate(rows):

        # 위경도 column이 None인 경우, 입력하지 않음
        action = {
                "_index": index_name,
                "_id": idx,   # db의 각 row에 대한 고유 ID로 변경 필요
                "발생일": row[0],
                "질병": row[1],
                "혈청형": row[2],
                "축종": row[3],
                "구분": row[4],
                "건수": row[5],
                "국가": row[6],
                "발생 지역": row[7],
                "위경도": row[8]
        }
        if row[8] == None:
            del action["위경도"]
        
        # indexing one document at a time
        # es.index(index=index_name, id=idx, doc_type="_doc", body=action)
        bulk_actions.append(action)

    # bulk indexing
    helpers.bulk(es, bulk_actions)


def pipe(opt):
    rows = read_from_db(opt.db_host, opt.db_user, opt.db_password, opt.db_table, display_rows=False)
    write_to_elastic(opt.es_host, opt.es_mapping, opt.es_index, rows)


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db_host", type=str, default="127.0.0.1")
    parser.add_argument("--db_user", type=str)
    parser.add_argument("--db_password", type=str)
    parser.add_argument("--db_table", type=str)
    parser.add_argument("--es_host", type=str, default="localhost:9200")
    parser.add_argument("--es_mapping", type=str)
    parser.add_argument("--es_index", type=str)
    opt = parser.parse_args()
    return opt


if __name__ == "__main__":
    opt = parse_opt()
    pipe(opt)