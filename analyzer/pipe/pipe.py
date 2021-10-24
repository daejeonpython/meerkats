import os
import argparse
import json
import time
from pprint import pprint
import pymysql
from elasticsearch.client import Elasticsearch
from elasticsearch import helpers
from utils.edit_distance import disease_convert, species_convert
from utils.en2kr_dict import disease_dict, species_dict


def read_mysql(opt):
    
    print('Reading data from db...')
    
    try:
        conn = pymysql.connect(host=opt.mysql_host, user=opt.mysql_user, password=opt.mysql_password)
        curs = conn.cursor()
        curs.execute('SHOW DATABASES')
        db_info = curs.fetchall()
        print(f'# Database information: {db_info}')

        curs.execute('SHOW TABLES FROM ' + opt.mysql_database)
        table_info = curs.fetchall()
        print(f'# List of tables of {opt.mysql_user}: {table_info}')
        target_table = opt.mysql_database + '.' + opt.mysql_table
        
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

            # 1. remove every linefeed & tap in strings (convert into space)
            if type(col) == str:                            
                row[idx] = col.replace('\n', ' ').replace('\t', ' ')
            # 2. convert unmapped English disease term into Korean disease term using Levenshtein distance
            if row[2] not in reverse_disease_dict:                
                row[2] = disease_convert(row[2].lower())
            # 3. convert unmapped English species term into Korean species term using Levenshtein distance
            if row[11] not in reverse_species_dict:
                row[11] = species_convert(row[11].lower())            

    return rows


def write_elastic(opt, rows):
    
    print('Writing extracted data into Elasticsearch...')
    es = Elasticsearch(hosts=[opt.es_host], http_auth=(opt.es_user, opt.es_password))
    with open(opt.es_mapping, 'r', encoding='utf-8') as json_file:
        mapping = json.load(json_file)

    if es.indices.exists(index=opt.es_index) is False:
        es.indices.create(index=opt.es_index, body=mapping)
    
    bulk_actions = []
  
    for row in rows:
        
        if row[18] != None:
            # Convert coordinate string into float list which is an acceptable form of Elasticsearch
            # ex) string: '[26.3, 27.3]' -> float list: [26.3, 27.3]
            row[18] = row[18].lstrip('[').rstrip(']').split(',')
            row[18] = [float(x) for x in row[18]]    
        
        action = {
                '_index': opt.es_index,
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
                '위경도': row[18],
        }
        # If the coordinate is None, remove from the document
        if row[18] == None:
            del action['위경도']
        
        bulk_actions.append(action)

    # bulk indexing
    helpers.bulk(es, bulk_actions)
    print('ES indexing is done.')


# Maintain sync between DB table and ES documnet
def sync(opt):

    es = Elasticsearch(hosts=[opt.es_host], http_auth=(opt.es_user, opt.es_password))
    res = helpers.scan(es, index=opt.es_index, query={'query': {'match_all': {}}})
    res = list(res)
    print(f'Number of ES documents: {len(res)}')

    try:
        conn = pymysql.connect(host=opt.mysql_host, user=opt.mysql_user, password=opt.mysql_password)
        curs = conn.cursor()
        table = opt.mysql_database + '.' + opt.mysql_table
        
        mismatched_ids = []
        outdated_preds = []
                    
        for idx, doc in enumerate(res):
            if idx % 1000 == 0:
                print(f'progress: ({idx}/{len(res)})')
    
            try:
                rowid = str(int(doc['_id']) + 1)  # _id of observation is always an integer            
                curs.execute("SELECT * FROM " + table + " WHERE rowid='" + rowid + "';")
    
                if curs.rowcount == 0:
                    with open(os.path.join('log', 'sync.log'), 'a', encoding='utf-8') as f:
                        current_time = time.strftime('%y/%m/%d\t%H:%M:%S', time.localtime())
                        f.write(f'{current_time}\tdeleted document\t{doc}\n')
                        mismatched_ids.append(doc['_id'])
            except:
                outdated_preds.append(doc['_id']) # _id of prediction is a random string
                
                    
        # Delete ES documnets that do not exist anymore in DB table
        res = es.delete_by_query(index=opt.es_index, body={'query': {'terms': {'_id': mismatched_ids}}})
        pprint(res)
        print(f'Number of mismatches between DB & ES: {len(mismatched_ids)}\n')
        # Delete outdated predictions
        res = es.delete_by_query(index=opt.es_index, body={'query': {'terms': {'_id': outdated_preds}}})
        pprint(res)
        print('Outdated predictions are deleted.')
        
            
    except Exception as ex:
        print(ex)


def write_csv(opt, rows, column_names):
    
    with open(opt.csv_path, 'w', encoding='utf-8') as f:
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


# read data from mysql, then insert them into elasticsearch & csv file
def pipe(opt):
    rows, column_names = read_mysql(opt)
    write_csv(opt, rows, column_names)
    sync(opt)
    write_elastic(opt, rows)


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
