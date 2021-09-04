import argparse
import json
import pymysql
from elasticsearch.client import Elasticsearch
from elasticsearch import helpers
from utils.edit_distance import disease_convert, species_convert
from utils.en2kr_dict import disease_dict, species_dict


def read_from_mysql(host, user, password, database, table):
    
    print('Reading data from db...')
    
    try:
        conn = pymysql.connect(host=host, user=user, password=password)
        curs = conn.cursor()
        curs.execute('SHOW DATABASES')
        db_info = curs.fetchall()
        print(f'# Database information: {db_info}')

        curs.execute('SHOW TABLES FROM ' + database)
        table_info = curs.fetchall()
        print(f'# List of tables of {user}: {table_info}')
        target_table = database + '.' + table
        
        curs.execute('SELECT * FROM ' + target_table)
        column_names = [x[0] for x in curs.description]
        print('# List of columns:')        
        for idx, col_name in enumerate(column_names):
            print(idx, col_name)
        
        rows = curs.fetchall()
        print(f'# Number of rows: {len(rows)}')
                
        return preprocess(rows), column_names
    
    except Exception as ex:
        print(ex)


def preprocess(rows):

    reverse_disease_dict = {value: key for (key, value) in disease_dict.items()}
    reverse_species_dict = {value: key for (key, value) in species_dict.items()}
    
    # tuple -> list
    rows = [list(x) for x in rows]
    for row in rows:        
        for idx, col in enumerate(row):

            # 1. remove every linefeed in strings (convert into space)
            if type(col) == str:                            
                row[idx] = col.replace('\n', ' ')
            # 2. convert unmapped English disease term into Korean disease term using Levenshtein distance
            if row[2] not in reverse_disease_dict:                
                row[2] = disease_convert(row[2].lower())
            # 3. convert unmapped English species term into Korean species term using Levenshtein distance
            if row[11] not in reverse_species_dict:
                row[11] = species_convert(row[11].lower())            

    return rows


def write_to_elastic(host, es_user, es_password, mapping_definition, index_name, rows):
    
    print('Writing extracted data into Elasticsearch...')
    es = Elasticsearch(hosts=[host], http_auth=(es_user, es_password))
    with open(mapping_definition, 'r', encoding='utf-8') as json_file:
        mapping = json.load(json_file)

    if es.indices.exists(index=index_name) is False:
        es.indices.create(index=index_name, body=mapping)
    
    bulk_actions = []
  
    for row in rows:
        
        if row[18] != None:
            # Convert coordinate string into float list which is an acceptable form of Elasticsearch
            # ex) string: '[26.3, 27.3]' -> float list: [26.3, 27.3]
            row[18] = row[18].lstrip('[').rstrip(']').split(',')
            row[18] = [float(x) for x in row[18]]    
        
        action = {
                '_index': index_name,
                '_id': row[0] - 1,  # current ES index (oie_reports_kr_ver2) _id starts from 0 while mysql db (oie_reports_kr) rowid starts from 1
                '발생일': row[8],
                '질병': row[2],
                '혈청형': row[5],
                '축종': row[11],
                '구분': row[10],
                '건수': row[7],
                '지역': row[3],
                '국가': row[4],
                '발생 지역': row[9],
                '위경도': row[18]
        }
        # If the coordinate is None, remove from the document
        if row[18] == None:
            del action['위경도']
        
        # indexing one document at a time
        # es.index(index=index_name, id=idx, doc_type='_doc', body=action)
        bulk_actions.append(action)

    # bulk indexing
    helpers.bulk(es, bulk_actions)
    print('ES indexing is done.')


def write_to_csv(path, rows, column_names):
    
    with open(path, 'w', encoding='utf-8') as f:
        for idx, col_name in enumerate(column_names):
            if idx != len(column_names) - 1:
                f.write(f'{col_name}\t')
            else:
                f.write(f'{col_name}\n')
        
        for row in rows:
            for idx, col in enumerate(row):
                if idx != len(row) - 1:
                    f.write(f'{col}\t')
                else:
                    f.write(f'{col}\n')
    
    print('csv file is generated.')


def pipe(opt):
    rows, column_names = read_from_mysql(opt.mysql_host, opt.mysql_user, opt.mysql_password, opt.mysql_database, opt.mysql_table)
    write_to_elastic(opt.es_host, opt.es_user, opt.es_password, opt.es_mapping, opt.es_index, rows)
    write_to_csv(opt.csv_path, rows, column_names)


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--mysql_host', type=str, default='127.0.0.1', help='MySQL host ip')
    parser.add_argument('--mysql_user', type=str, help='MySQL user name')
    parser.add_argument('--mysql_password', type=str, help='MySQL password')
    parser.add_argument('--mysql_database', type=str, help='database name')
    parser.add_argument('--mysql_table', type=str, help='table name')
    parser.add_argument('--es_host', type=str, default='localhost:9200', help='elasticsearch host ip')
    parser.add_argument('--es_user', type=str, help='elasticsearch user name')
    parser.add_argument('--es_password', type=str, help='elsticsearch password')
    parser.add_argument('--es_mapping', type=str, help='index mappping defintion')
    parser.add_argument('--es_index', type=str, help='index name')
    parser.add_argument('--csv_path', type=str, help='path to csv file')
    opt = parser.parse_args()

    pipe(opt)
