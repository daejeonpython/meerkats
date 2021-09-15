import os
import argparse
import numpy as np
import matplotlib.pyplot as plt

import torch
from torch.utils.data import DataLoader

from utils.datasets import create_dataset
from models.gru import StackedGRU


def predict(opt):
    
    device = opt.device    

    with open(opt.weight, 'rb') as f:
        saved_model = torch.load(f)
    scaler = saved_model['scaler']
    seq_len = saved_model['seq_len']
    print(f"best epoch: {saved_model['best_epoch']}")

    df, validation_dataset = create_dataset(opt.data, is_train=False, scaler=scaler, split_ratio=opt.split_ratio, seq_len=seq_len)
    dataloader = DataLoader(validation_dataset, batch_size=opt.batch_size)
    
    
    model = StackedGRU(n_features=df.shape[1])
    model.load_state_dict(saved_model['state'])    
    model.eval()
    model.to(device)

    preds = []
    with torch.no_grad():

        if opt.autoregressive:
            # Feed prediction result back to input            
            for i, (x, _) in enumerate(dataloader):
                test_seq = x  # test_seq.shape = (1, 10, 1)
                break
            
            for i in range(len(dataloader)):
                y_pred = model(test_seq.to(device))  # y_pred.shape = (1, 1)
                y_pred = torch.flatten(y_pred).item()  # y_pred = scalar value
                preds.append(y_pred)
                new_seq = test_seq.numpy().flatten()  # new_seq.shape = (10, )
                new_seq = np.append(new_seq, [y_pred])  # new_seq.shape = (11, )
                new_seq = new_seq[1:]  # new_seq.shape = (10, )
                test_seq = torch.as_tensor(new_seq).view(1, seq_len, 1).float()  # test_seq.shape = (1, 10, 1)
        
        else:            
            for i, (x, _) in enumerate(dataloader):                
                y_pred = model(x.to(device))   # y_pred.shape = (1, 1)
                y_pred = torch.flatten(y_pred).item()  # y_pred = scalar value
                preds.append(y_pred)

    visualize(df, scaler, preds, seq_len, opt.show_observed_cases)
        

def visualize(df, scaler, preds, seq_len, show_observed_cases):
    
    predicted_cases = scaler.inverse_transform(np.expand_dims(preds, axis=0)).flatten()                
    train_data_size = len(df) - int(len(df) * opt.split_ratio)
    
    plt.figure(figsize=(12, 8))
    plt.title('Prediction Graph')
    plt.xlabel('timestamp')
    plt.ylabel('number of outbreaks')
    
    if show_observed_cases:
        plt.plot(df.index[:train_data_size], df['outbreaks'][:train_data_size], label='Observed Daily Cases')
    plt.plot(df.index[train_data_size:(len(df) - seq_len - 1)], df['outbreaks'][train_data_size:(len(df) - seq_len - 1)], label='True Cases')
    plt.plot(df.index[train_data_size:(len(df) - seq_len - 1)], predicted_cases, label='Predicted Cases')        
    plt.legend()
    plt.savefig(os.path.join('runs', 'prediction.png'))
    plt.show()



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