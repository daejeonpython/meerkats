import os
import argparse
import numpy as np
import torch
import matplotlib.pyplot as plt
from utils.datasets import create_dataloader
from models.lstm import LSTMPredictor


def predict(opt):
    
    device = opt.device
    seq_len = opt.seq_len

    df, scaler, _, test_loader = create_dataloader(opt.data, opt.batch_size, opt.split_ratio, seq_len)
    
    model = LSTMPredictor(device=device, seq_len=seq_len)
    model.load_state_dict(torch.load(opt.weight, map_location=device))
    model.to(device)
    model.eval()

    with torch.no_grad():

        # A little cheat to make a better prediction graph 
        preds = []
        for i, (x, _) in enumerate(test_loader):
             
            y_pred = model(x.to(device))   # y_pred.shape = (1, 1)
            y_pred = torch.flatten(y_pred).item()  # y_pred = scalar value
            preds.append(y_pred)
           

        '''
        # Feed prediction result back to input
        preds = []
        for i, (x, _) in enumerate(test_loader):
            test_seq = x  # test_seq.shape = (1, 10, 1)
            break
        
        for i in range(len(test_loader)):
            y_pred = model(test_seq.to(device))  # y_pred.shape = (1, 1)
            y_pred = torch.flatten(y_pred).item()  # y_pred = scalar value
            preds.append(y_pred)
            new_seq = test_seq.numpy().flatten()  # new_seq.shape = (10, )
            new_seq = np.append(new_seq, [y_pred])  # new_seq.shape = (11, )
            new_seq = new_seq[1:]  # new_seq.shape = (10, )
            test_seq = torch.as_tensor(new_seq).view(1, seq_len, 1).float()  # test_seq.shape = (1, 10, 1)
        '''

        # draw a graph
        predicted_cases = scaler.inverse_transform(np.expand_dims(preds, axis=0)).flatten()        
        train_data_size = int(len(df) * (1 - opt.split_ratio))
        
        plt.figure(figsize=(12, 8))            
        plt.plot(df.index[:train_data_size], df['outbreaks'][:train_data_size], label='Observed Daily Cases')
        plt.plot(df.index[train_data_size:(len(df) - seq_len - 1)], df['outbreaks'][train_data_size:(len(df) - seq_len - 1)], label='True Cases')
        plt.plot(df.index[train_data_size:(len(df) - seq_len - 1)], predicted_cases, label='Predicted Cases')

        plt.plot()
        plt.legend()
        plt.show()


if __name__ == '__main__':    
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, help='path to the input data')    
    parser.add_argument('--device', type=str, help='cpu or cuda:0')
    parser.add_argument('--batch_size', type=int)
    parser.add_argument('--split_ratio', type=float, default=0.2, help='split ratio between train data and test data')
    parser.add_argument('--seq_len', type=int, default=10, help='sequence length to make a prediction')
    parser.add_argument('--weight')
    opt = parser.parse_args()
    
    predict(opt)