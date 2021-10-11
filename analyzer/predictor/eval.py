import argparse
import easydict
import math
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from scipy.stats import pearsonr

import torch
from utils.datasets import create_dataloader
from utils.preprocessor import csv_to_pd
from utils.plots import plot_eval_result
from models.transformer import transformer


def eval(opt):
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'    

    with open(opt.weight, 'rb') as f:
        saved_model = torch.load(f)
    scaler = saved_model['scaler']
    window_size = saved_model['window_size']
    ahead = saved_model['ahead']
    print(f"best epoch: {saved_model['best_epoch']}")
    print(f"window_size: {window_size}")
    print(f'ahead: {ahead}')

    observed_df = csv_to_pd(opt.train_data)
    test_df, dataloader = create_dataloader(opt.test_data, is_train=False, scaler=scaler, batch_size=opt.batch_size, window_size=window_size, ahead=ahead) 

    model_args = easydict.EasyDict({
        'output_size': saved_model['output_size'],
        'window_size': window_size,
        'ahead': ahead,
        'batch_size': opt.batch_size,        
        'e_features': saved_model['e_features'],
        'd_features': saved_model['d_features'],
        'd_hidn': saved_model['d_hidn'],
        'n_head': saved_model['n_head'],
        'd_head': saved_model['d_head'],
        'dropout': saved_model['dropout'],
        'd_ff': saved_model['d_ff'],
        'n_layer': saved_model['n_layer'],
        'dense_h': saved_model['dense_h'],        
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
                test_seq = x.to(device)  # test_seq.shape = (1, window_size, n_features)  ex) (1, 10, 4)                
                break
            
            for i, (x, y) in enumerate(dataloader):
                y_pred = model(test_seq, test_seq)  # y_pred.shape = (1, n_features)  ex) (1, 4)                                                
                preds.append(y_pred)                

                new_seq = torch.cat((test_seq, y_pred.unsqueeze(axis=0)), 1)  # new_seq.shape = (1, window_size + 1, n_features)  ex) (1, 11, 4)                
                new_seq = new_seq[:, 1:, :]  # new_seq.shape = (1, 10, 4)                
                test_seq = new_seq                
        
        else:            
            for i, (x, y) in enumerate(dataloader):                                                                            
                y_pred = model(x.to(device), x.to(device))   # y_pred.shape = (batch_size, ahead. n_features)  ex) (1, 2, 4)                                                                                
                preds.append(y_pred)
    
    preds = torch.stack(preds).squeeze(axis=1)  # (len(test_df) - window_size - ahead, ahead, n_features)
    df_preds = []

    for i in range(ahead):
        df_preds.append(pd.DataFrame(preds[:,i,:].cpu().numpy(), columns=test_df.columns))        


    for col in test_df.columns:
        print(col)
        
        predicted_cases = scaler.inverse_transform(np.expand_dims(df_preds[0][col], axis=0)).flatten()
        true_cases = np.array(test_df[col])
        true_cases = true_cases[(window_size + 1):len(true_cases) + 1 - ahead]  # ahead = 1

        print(f'pearson correlation coefficient: {pearsonr(true_cases, predicted_cases)}')        
        print(f'root mean squared error (RMSE): {math.sqrt(mean_squared_error(true_cases, predicted_cases))}')
        print(f'mean absolute error (MAE): {mean_absolute_error(true_cases, predicted_cases)}\n')

        plot_eval_result(observed_df, test_df, predicted_cases, col, window_size, ahead, show_observed_cases=True)
        plot_eval_result(observed_df, test_df, predicted_cases, col, window_size, ahead, show_observed_cases=False)
        

if __name__ == '__main__':    
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--train_data', type=str, default='data/train/train.csv', help='path to the observed (train) data only for visualization')
    parser.add_argument('--test_data', type=str, help='path to the test data')    
    parser.add_argument('--batch_size', type=int)
    parser.add_argument('--weight', type=str, help='path to the weight file')
    parser.add_argument('--autoregressive', action='store_true')    
    opt = parser.parse_args()
    
    eval(opt)