import os
import argparse
import easydict
import math
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score, mean_absolute_error, median_absolute_error, mean_squared_error, mean_absolute_percentage_error
from scipy.stats import pearsonr

import torch
from utils.datasets import create_dataloader
from utils.preprocessor import csv_to_pd
from utils.plots import plot_result
from models.transformer import transformer


def predict(opt):
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    with open(opt.weight, 'rb') as f:
        saved_model = torch.load(f)
    scaler = saved_model['scaler']
    seq_len = saved_model['seq_len']
    print(f"best epoch: {saved_model['best_epoch']}")
    print(f"seq_len: {saved_model['seq_len']}")

    observed_df = csv_to_pd(opt.train_data)
    test_df, dataloader = create_dataloader(opt.test_data, is_train=False, scaler=scaler, batch_size=opt.batch_size, seq_len=seq_len)        

    model_args = easydict.EasyDict({
        'output_size': test_df.shape[-1],
        'window_size': seq_len,
        'batch_size': opt.batch_size,        
        'e_features': test_df.shape[-1],
        'd_features': test_df.shape[-1],
        'd_hidn': 128,
        'n_head': 4,
        'd_head': 32,
        'dropout': 0.2,
        'd_ff': 128,
        'n_layer': 3,
        'dense_h': 128,        
        'device': device
    })

    model = transformer(model_args).to(device)
    model.load_state_dict(saved_model['state'])    
    model.eval()    

    preds = []    
    with torch.no_grad():

        if opt.autoregressive:
            # Feed prediction result back to input            
            for i, (x, _) in enumerate(dataloader):
                test_seq = x.to(device)  # test_seq.shape = (1, seq_len, n_features)  ex) (1, 10, 4)                
                break
            
            for i, (x, y) in enumerate(dataloader):
                y_pred = model(test_seq, test_seq)  # y_pred.shape = (1, n_features)  ex) (1, 4)                                                
                preds.append(y_pred)                

                new_seq = torch.cat((test_seq, y_pred.unsqueeze(axis=0)), 1)  # new_seq.shape = (1, seq_len + 1, n_features)  ex) (1, 11, 4)                
                new_seq = new_seq[:, 1:, :]  # new_seq.shape = (1, 10, 4)                
                test_seq = new_seq                
        
        else:            
            for i, (x, y) in enumerate(dataloader):                                                                            
                y_pred = model(x.to(device), x.to(device))   # y_pred.shape = (1, n_features)  ex) (1, 4)                                                                                
                preds.append(y_pred)
    
    preds = torch.stack(preds).squeeze(axis=1)
    preds = pd.DataFrame(preds.cpu().numpy(), columns=test_df.columns)        

    evaluate(observed_df, test_df, scaler, preds, seq_len)


def evaluate(observed_df, test_df, scaler, preds, seq_len):
    
    for col in test_df.columns:
        print(col)
        
        predicted_cases = scaler.inverse_transform(np.expand_dims(preds[col], axis=0)).flatten()
        true_cases = np.array(test_df[col])
        true_cases = true_cases[seq_len + 1:]

        print(f'pearson correlation coefficient: {pearsonr(true_cases, predicted_cases)}')
        print(f'r2 score: {r2_score(true_cases, predicted_cases)}')        
        print(f'mean absolute error (MAE): {mean_absolute_error(true_cases, predicted_cases)}')        
        print(f'median absolute error: {median_absolute_error(true_cases, predicted_cases)}')
        print(f'mean squared error (MSE): {mean_squared_error(true_cases, predicted_cases)}')
        print(f'root mean squared error (RMSE): {math.sqrt(mean_squared_error(true_cases, predicted_cases))}')
        print(f'mean absolute percentage error (MAPE): {mean_absolute_percentage_error(true_cases, predicted_cases)}\n')
                
        plot_result(observed_df, test_df, predicted_cases, col, seq_len, show_observed_cases=True)
        plot_result(observed_df, test_df, predicted_cases, col, seq_len, show_observed_cases=False)
        

if __name__ == '__main__':    
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--train_data', type=str, default='data/train/train.csv', help='path to the observed (train) data only for visualization')
    parser.add_argument('--test_data', type=str, help='path to the test data')    
    parser.add_argument('--batch_size', type=int)
    parser.add_argument('--weight', type=str, help='path to the weight file')
    parser.add_argument('--autoregressive', action='store_true')    
    opt = parser.parse_args()
    
    predict(opt)