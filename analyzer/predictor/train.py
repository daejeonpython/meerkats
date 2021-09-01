import os
import argparse
import numpy as np
import torch
import matplotlib.pyplot as plt
from utils.datasets import create_dataset
from models.lstm import LSTMPredictor


def train(opt):
    
    split_ratio = 0.2
    seq_len = 10    
    device = opt.device

    _, _, _, _, train_points, train_labels, test_points, test_labels = create_dataset(opt.data, split_ratio, seq_len)
    train_points = torch.from_numpy(train_points).float().to(device)
    train_labels = torch.from_numpy(train_labels).float().to(device)
    test_points = torch.from_numpy(test_points).float().to(device)
    test_labels = torch.from_numpy(test_labels).float().to(device)

    model = LSTMPredictor(seq_len=seq_len)
    model.to(device)
    model.train()

    loss_fn = torch.nn.MSELoss(reduction='sum')
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
    num_epochs = 300

    train_hist = np.zeros(num_epochs)
    test_hist = np.zeros(num_epochs)

    
    for epoch in range(num_epochs):
        
        y_pred = model(train_points) 
        loss = loss_fn(y_pred, train_labels)
        train_hist[epoch] = loss.item()

        with torch.no_grad():            
            y_test_pred = model(test_points)
            test_loss = loss_fn(y_test_pred, test_labels)
            test_hist[epoch] = test_loss.item()
        
            if epoch % 10 == 0:
                print(f'Epoch {epoch} train loss: {loss.item()} test loss: {test_loss.item()}')
    
        optimizer.zero_grad()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5)
        loss.backward()        
        optimizer.step()

        wdir = 'runs/train'
        if (epoch + 1) % opt.save_period == 0:                        
            torch.save(model.state_dict(), os.path.join(wdir,str(epoch + 1) + "_epochs.pt"))        
        

    plt.figure(figsize=(30, 40))
    plt.plot(train_hist, label="Training Loss")
    plt.plot(test_hist, label="Test Loss")
    plt.legend()
    plt.savefig(os.path.join('runs', 'train', 'loss.png'))
    plt.cla()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, help="path to the input data")    
    parser.add_argument("--device", type=str, default="cpu", help="cuda:0 or cpu")
    parser.add_argument("--project", default="runs/train", help="save to project/name")
    parser.add_argument("--save_period", type=int, default=10, help='log model after every "save_period" epochs')
    opt = parser.parse_args()

    train(opt)
