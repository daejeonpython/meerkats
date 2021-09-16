import os
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import torch
from utils.datasets import create_dataloader
from models.gru import StackedGRU


def predict(opt):
    
    device = opt.device    

    with open(opt.weight, 'rb') as f:
        saved_model = torch.load(f)
    scaler = saved_model['scaler']
    seq_len = saved_model['seq_len']
    print(f"best epoch: {saved_model['best_epoch']}")

    df, dataloader = create_dataloader(opt.data, is_train=False, scaler=scaler, batch_size=opt.batch_size, split_ratio=opt.split_ratio, seq_len=seq_len)    
    
    
    model = StackedGRU(n_features=df.shape[-1])
    model.load_state_dict(saved_model['state'])    
    model.eval()
    model.to(device)

    preds = []
    with torch.no_grad():

        if opt.autoregressive:
            # Feed prediction result back to input            
            for i, (x, _) in enumerate(dataloader):
                test_seq = x.to(device)  # test_seq.shape = (1, seq_len, n_features)  ex) (1, 10, 4)                
                break
            
            for i in range(len(dataloader)):
                y_pred = model(test_seq)  # y_pred.shape = (1, n_features)  ex) (1, 4)                
                preds.append(y_pred)                
                new_seq = torch.cat((test_seq, y_pred.unsqueeze(axis=0)), 1)  # new_seq.shape = (1, seq_len + 1, n_features)  ex) (1, 11, 4)                
                new_seq = new_seq[:, 1:, :]  # new_seq.shape = (1, 10, 4)                
                test_seq = new_seq                
        
        else:            
            for i, (x, _) in enumerate(dataloader):                
                y_pred = model(x.to(device))   # y_pred.shape = (1, n_features)  ex) (1, 4)                
                preds.append(y_pred)

    preds = torch.stack(preds).squeeze(axis=1)
    preds = pd.DataFrame(preds.cpu().numpy(), columns=df.columns)
    visualize(df, scaler, preds, seq_len, opt.show_observed_cases)
        

def visualize(df, scaler, preds, seq_len, show_observed_cases):
    
    for col in df.columns:
        print(col)
        
        predicted_cases = scaler.inverse_transform(np.expand_dims(preds[col], axis=0)).flatten()                
        train_data_size = len(df) - int(len(df) * opt.split_ratio)
        
        plt.figure(figsize=(12, 8))
        plt.title(f'Prediction Graph in {col}')
        plt.xlabel('timestamp')
        plt.ylabel('number of outbreaks')
        
        if show_observed_cases:
            plt.plot(df.index[:train_data_size], df[col][:train_data_size], label='Observed Daily Cases')
        plt.plot(df.index[train_data_size:(len(df) - seq_len - 1)], df[col][train_data_size:(len(df) - seq_len - 1)], label='True Cases')
        plt.plot(df.index[train_data_size:(len(df) - seq_len - 1)], predicted_cases, label='Predicted Cases')        
        plt.legend()
        plt.savefig(os.path.join('runs', f'{col}_prediction.png'))
        # plt.show()



if __name__ == '__main__':    
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, help='path to the input data')    
    parser.add_argument('--device', type=str, help='cpu or cuda:0')
    parser.add_argument('--batch_size', type=int)
    parser.add_argument('--split_ratio', type=float, default=0.2, help='split ratio between train data and test data')    
    parser.add_argument('--weight', type=str, help='path to the weight file')
    parser.add_argument('--autoregressive', action='store_true')
    parser.add_argument('--show_observed_cases', action='store_true')
    opt = parser.parse_args()
    
    predict(opt)