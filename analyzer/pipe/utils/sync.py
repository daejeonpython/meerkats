import argparse
import pymysql
from elasticsearch.client import Elasticsearch
from elasticsearch.helpers import scan

def verify(opt):

    es = Elasticsearch(hosts=[opt.es_host], http_auth=(opt.es_user, opt.es_password))

    res = scan(es, index=opt.es_index, query={'query': {'match_all': {}}})
    res = list(res)
    print(f'Number of es documents: {len(res)}')

    '''
    with open('index_snapshot.txt', 'w', encoding='utf-8') as f:
        for idx, doc in enumerate(res):
            f.write(f'{doc}\n')
    '''

    try:
        conn = pymysql.connect(host=opt.mysql_host, user=opt.mysql_user, password=opt.mysql_password)
        curs = conn.cursor()
        table = opt.mysql_database + '.' + opt.mysql_table
        n_mismatches = 0
        
        with open('mismatch.txt', 'w', encoding='utf-8') as f:
            
            for idx, doc in enumerate(res):
                if idx % 100 == 0:
                    print(f'progress: ({idx}/{len(res)})')
    
                curs.execute('SELECT * FROM ' + table + ' WHERE rowid=' + str(int(doc['_id']) + 1))
                rows = curs.fetchall()
    
                if curs.rowcount == 0:
                    f.write(f'{doc}\n')
                    n_mismatches += 1
        
        print(f'number of mismatches between DB & ES: {n_mismatches}')
            
    except Exception as ex:
        print(ex)
    

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--mysql_host', type=str, default='127.0.0.1')
    parser.add_argument('--mysql_user', type=str)
    parser.add_argument('--mysql_password', type=str)
    parser.add_argument('--mysql_database', type=str)
    parser.add_argument('--mysql_table', type=str)
    parser.add_argument('--es_host', type=str, default='localhost:9200')
    parser.add_argument('--es_user', type=str)
    parser.add_argument('--es_password', type=str)
    parser.add_argument('--es_index', type=str)
    opt = parser.parse_args()
    
    verify(opt)

