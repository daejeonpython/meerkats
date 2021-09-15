import os
import math
import argparse
import numpy as np
import matplotlib.pyplot as plt

import torch

from utils.datasets import create_dataloader
from models.gru import StackedGRU


def train(opt):
    
    device = opt.device
    epochs = opt.epochs
    seq_len = opt.seq_len

    df, train_loader, scaler = create_dataloader(opt.data, is_train=True, scaler=None, batch_size=opt.batch_size, split_ratio=opt.split_ratio, seq_len=seq_len)
    _, val_loader = create_dataloader(opt.data, is_train=False, scaler=scaler, batch_size=opt.batch_size, split_ratio=opt.split_ratio, seq_len=seq_len)
        

    model = StackedGRU(n_features=df.shape[1])
    print(model)
    model.train()
    model.to(device)
        
    optimizer = torch.optim.AdamW(model.parameters())    
    loss_fn = torch.nn.MSELoss()
    # loss_fn = torch.nn.MSELoss(reduction='sum')
    
    best = {'loss': math.inf}
    train_hist = np.zeros(epochs)
    validation_hist = np.zeros(epochs)
    
    for epoch in range(epochs):

        # train
        train_loss = 0
        for bs, (x, y) in enumerate(train_loader):            
            optimizer.zero_grad()
            x = x.to(device)
            y = y.to(device)            
            y_pred = model(x)            
            loss = loss_fn(y_pred, y)                        
            loss.backward()                        
            train_loss += loss.item()
            optimizer.step()
            
        train_hist[epoch] = train_loss

        # validation        
        with torch.no_grad():
            validation_loss = 0
            for bs, (x, y) in enumerate(val_loader):  
                x = x.to(device)
                y = y.to(device)
                y_pred = model(x)
                loss = loss_fn(y_pred, y)
                validation_loss += loss.item()
            
            validation_hist[epoch] = validation_loss

        print(f'epoch: {epoch}, train_loss: {train_loss}, val_loss: {validation_loss}')
        if validation_loss < best['loss']:
            best['state'] = model.state_dict()
            best['loss'] = validation_loss
            best['epoch'] = epoch + 1
        
            with open(os.path.join('runs', 'best.pt'), 'wb') as f:
                torch.save(
                    {
                        'state': best['state'],
                        'best_epoch': best['epoch'],
                        'train_hist': train_hist,
                        'validation_hist': validation_hist,
                        'scaler': scaler,
                        'seq_len': seq_len,                        
                    },
                    f,
                )        
        
    plt.figure(figsize=(16, 4))
    plt.title('Training Loss Graph')
    plt.xlabel('epochs')
    plt.ylabel('loss')
    plt.plot(train_hist, label='Training Loss')
    plt.plot(validation_hist, label='Validation Loss')
    plt.legend()
    plt.savefig(os.path.join('runs', 'loss.png'))
    plt.show()    


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, help='path to the input data')    
    parser.add_argument('--device', type=str, help='cpu or cuda:0')
    parser.add_argument('--epochs', type=int, help='number of epochs')
    parser.add_argument('--batch_size', type=int, help='batch size')
    parser.add_argument('--split_ratio', type=float, default=0.2, help='split ratio between train data and test data')
    parser.add_argument('--seq_len', type=int, default=10, help='sequence length to make a prediction')
    # parser.add_argument('--project', type=str, default='runs/train', help='save to project/name')
    # parser.add_argument('--save_period', type=int, default=10, help="log model after every 'save_period' epochs")
    opt = parser.parse_args()
    train(opt)
