import os
import argparse
import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt
from utils.datasets import create_dataloader
from models.lstm import LSTMPredictor


def predict(opt):
    seq_len = 10
    split_ratio = 0.2
    # train_loader, test_loader = create`_dataloader(opt.data, split_ratio, seq_len)
    df, train_data, test_data, train_dataset, test_dataset = create_dataloader(opt.data, split_ratio, seq_len)
    model = LSTMPredictor(n_features=1, n_hidden=512, seq_len=seq_len, n_layers=2, device=opt.device)
    model.load_state_dict(torch.load(opt.weight, map_location=opt.device))
    model.to(opt.device)
    model.eval()

    train_points, train_labels = train_dataset[0]
    test_points, test_labels = test_dataset[0]

    with torch.no_grad():
        
        preds = []
        for i in range(len(test_points)):
            test_seq = test_points[i:i+1]
            test_seq = torch.from_numpy(test_seq).float()
            
            y_test_pred = model(test_seq.to(opt.device))  # y_test_pred.shape = torch.Size([1, 1])            
            pred = torch.flatten(y_test_pred).item()
            preds.append(pred)

        true_cases = test_dataset.scaler.inverse_transform(np.expand_dims(test_labels.flatten(), axis=0)).flatten()
        predicted_cases = test_dataset.scaler.inverse_transform(np.expand_dims(preds, axis=0)).flatten()
        # print(true_cases)
        # print(predicted_cases)

        plt.figure(figsize=(12, 8))
        plt.plot(df.index[:len(train_data)], train_data, label="Historical Daily Cases")
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