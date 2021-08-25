import argparse
import json
import pymysql
from elasticsearch.client import Elasticsearch
from elasticsearch import helpers
from utils.edit_distance import disease_convert, species_convert
from utils.en2kr_dict import disease_dict, species_dict


def read_from_mysql(host, user, password, database, table, display_rows=False):
    
    print("Reading data from db...")
    reverse_disease_dict = {value: key for (key, value) in disease_dict.items()}
    reverse_species_dict = {value: key for (key, value) in species_dict.items()}

    try:
        conn = pymysql.connect(host=host, user=user, password=password)
        curs = conn.cursor()
        curs.execute("SHOW DATABASES")
        db_info = curs.fetchall()
        print(f'# Database information: {db_info}')

        curs.execute("SHOW TABLES FROM " + database)
        table_info = curs.fetchall()
        print(f'# List of tables of {user}: {table_info}')
        target_table = database + "." + table
        
        curs.execute("SELECT * FROM " + target_table)
        column_info = curs.description
        print("# List of columns:")        
        for idx, col in enumerate(column_info):
            print(idx, col[0])

        curs.execute("SELECT rowid, 발생일, 질병, 혈청형, 축종, 구분, 건수, 지역, 국가, `발생 지역`, 위경도 FROM " + target_table)
        rows = curs.fetchall()
        # tuple -> list
        rows = [list(x) for x in rows]

        for idx, row in enumerate(rows):
            if row[2] not in reverse_disease_dict:                
                row[2] = disease_convert(row[2])
            if row[4] not in reverse_species_dict:
                row[4] = species_convert(row[4])
            if row[10] != None:
                # ex) string: "[26.3, 27.3]" -> float list: [26.3, 27.3]
                row[10] = row[10].lstrip("[").rstrip("]").split(",")
                row[10] = [float(x) for x in row[10]]
            if display_rows:
                print(idx, row)
            
        print(f'# Number of rows: {len(rows)}')
        return rows
    
    except Exception as ex:
        print(ex)


def write_to_elastic(host, es_user, es_password, mapping_definition, index_name, rows):
    
    print("Writing extracted data into Elasticsearch...")
    es = Elasticsearch(hosts=[host], http_auth=(es_user, es_password))
    with open(mapping_definition, "r", encoding="utf-8") as json_file:
        mapping = json.load(json_file)

    if es.indices.exists(index=index_name) is False:
        es.indices.create(index=index_name, body=mapping)
    
    bulk_actions = []
    for row in rows:

        # 위경도 column이 None인 경우, 입력하지 않음
        action = {
                "_index": index_name,
                "_id": row[0] - 1,  # current ES index (oie_reports_kr_ver2) _id starts from 0 while mysql db (oie_reports_kr) rowid starts from 1
                "발생일": row[1],
                "질병": row[2],
                "혈청형": row[3],
                "축종": row[4],
                "구분": row[5],
                "건수": row[6],
                "지역": row[7],
                "국가": row[8],
                "발생 지역": row[9],
                "위경도": row[10]
        }
        if row[10] == None:
            del action["위경도"]
        
        # indexing one document at a time
        # es.index(index=index_name, id=idx, doc_type="_doc", body=action)
        bulk_actions.append(action)

    # bulk indexing
    helpers.bulk(es, bulk_actions)


def write_to_csv(rows, path):
    
    with open(path, "w", encoding="utf-8") as f:
        f.write("발생일\t질병\t혈청형\t축종\t구분\t건수\t지역\t국가\t발생 지역\t위경도\n")
        for row in rows:
            for idx, col in enumerate(row):
                if idx != len(row) - 1:
                    f.write(f'{col}\t')
                else:
                    f.write(f'{col}\n')
            
def pipe(opt):
    rows = read_from_mysql(opt.mysql_host, opt.mysql_user, opt.mysql_password, opt.mysql_database, opt.mysql_table, display_rows=False)
    write_to_elastic(opt.es_host, opt.es_user, opt.es_password, opt.es_mapping, opt.es_index, rows)
    write_to_csv(rows, opt.csv_path)


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mysql_host", type=str, default="127.0.0.1", help="MySQL host ip")
    parser.add_argument("--mysql_user", type=str, help="MySQL user name")
    parser.add_argument("--mysql_password", type=str, help="MySQL password")
    parser.add_argument("--mysql_database", type=str, help="database name")
    parser.add_argument("--mysql_table", type=str, help="table name")
    parser.add_argument("--es_host", type=str, default="localhost:9200", help="elasticsearch host ip")
    parser.add_argument("--es_user", type=str, help="elasticsearch user name")
    parser.add_argument("--es_password", type=str, help="elsticsearch password")
    parser.add_argument("--es_mapping", type=str, help="index mappping defintion")
    parser.add_argument("--es_index", type=str, help="index name")
    parser.add_argument("--csv_path", type=str, help="path to csv file")
    opt = parser.parse_args()
    return opt


if __name__ == "__main__":
    opt = parse_opt()
    pipe(opt)
