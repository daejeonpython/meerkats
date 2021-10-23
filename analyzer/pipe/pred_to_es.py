import argparse
import json
import pandas as pd
from elasticsearch.client import Elasticsearch
from elasticsearch import helpers


def pred_to_es(opt):
    
    pred_df = pd.read_csv(opt.pred_data, sep='\t')
    pred_df.set_index('timestamp', inplace=True)
    print(pred_df)    

    bulk_actions = []
    
    for col in pred_df.columns:
        for i in range(len(pred_df[col])):
            action = {
                '_index': opt.es_index,
                '발생일': pred_df.index[i],
                '질병': opt.target_disease,
                '예측건수': max(pred_df[col][i], 0),
                '국가': col,
            }
            bulk_actions.append(action)
    
    
    es = Elasticsearch(hosts=[opt.es_host], http_auth=(opt.es_user, opt.es_password))
    with open(opt.es_mapping, 'r', encoding='utf-8') as json_file:
        mapping = json.load(json_file)

    if es.indices.exists(index=opt.es_index) is False:
        es.indices.create(index=opt.es_index, body=mapping)
    
    result = helpers.bulk(es, bulk_actions)
    print(result)


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()

    parser.add_argument('--es_host', type=str, default='localhost:9200', help='elasticsearch host ip')
    parser.add_argument('--es_user', type=str, help='elasticsearch user name')
    parser.add_argument('--es_password', type=str, help='elsticsearch password')
    parser.add_argument('--es_mapping', type=str, help='index mappping defintion')
    parser.add_argument('--es_index', type=str, help='index name')        
    parser.add_argument('--pred_data', type=str, help='path to the prediction result')
    parser.add_argument('--target_disease', type=str, help='target disease to predict')
    
    opt = parser.parse_args()
    pred_to_es(opt)
