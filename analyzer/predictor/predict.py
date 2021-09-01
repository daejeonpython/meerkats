import os
import argparse
import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt
from utils.datasets import create_dataset
from models.lstm import LSTMPredictor


def predict(opt):
    
    split_ratio = 0.2
    seq_len = 10
    device = opt.device

    # train_loader, test_loader = create_dataloader(opt.data, split_ratio, seq_len)
    df, scaler, train_data, _, _, _, test_points, test_labels = create_dataset(opt.data, split_ratio, seq_len)
    test_points = torch.from_numpy(test_points).float().to(device)
    test_labels = torch.from_numpy(test_labels).float().to(device)

    model = LSTMPredictor(seq_len=seq_len)
    model.load_state_dict(torch.load(opt.weight, map_location=device))
    model.to(device)
    model.eval()


    with torch.no_grad():
        
        preds = []
        for i in range(len(test_points)):
                    
            test_seq = test_points[i:i+1]            
            
            y_test_pred = model(test_seq)  # y_test_pred.shape = torch.Size([1, 1])            
            pred = torch.flatten(y_test_pred).item()
            preds.append(pred)            
          
          
        true_cases = scaler.inverse_transform(np.expand_dims(test_labels.flatten(), axis=0)).flatten()
        predicted_cases = scaler.inverse_transform(np.expand_dims(preds, axis=0)).flatten()
       
        plt.figure(figsize=(12, 8))
        plt.plot(df.index[:len(train_data)], scaler.inverse_transform(train_data).flatten(), label="Historical Daily Cases")
        plt.plot(df.index[len(train_data):len(train_data) + len(true_cases)], true_cases, label="Real Daily Cases")
        plt.plot(df.index[len(train_data):len(train_data) + len(true_cases)], predicted_cases, label="Predicted Daily Cases")
        plt.legend()
        plt.show()



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, help="path to the input data")    
    parser.add_argument("--device", type=str, default="cpu", help="cuda:0 or cpu")
    parser.add_argument("--weight")
    opt = parser.parse_args()

    predict(opt)