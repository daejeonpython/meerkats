import os
import argparse
import numpy as np
import torch
import matplotlib.pyplot as plt
from utils.datasets import create_dataloader
from models.lstm import LSTMPredictor


def train(opt):
    
    device = opt.device
    epochs = opt.epochs
    seq_len = opt.seq_len

    _, _, train_loader, test_loader = create_dataloader(opt.data, opt.batch_size, opt.split_ratio, seq_len)

    model = LSTMPredictor(device=device, seq_len=seq_len)
    model.to(device)
    model.train()

    loss_fn = torch.nn.MSELoss(reduction='sum')
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)    

    train_hist = np.zeros(epochs)
    test_hist = np.zeros(epochs)

    for epoch in range(epochs):

        # train
        train_loss = 0
        for bs, (x, y) in enumerate(train_loader):
            x = x.to(device)
            y = y.to(device)

            optimizer.zero_grad()
            
            y_pred = model(x)
            model.reset_states()
            loss = loss_fn(y_pred, y)            
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5)
            loss.backward()                        
            optimizer.step()

            train_loss += loss.item()

        train_hist[epoch] = train_loss


        # validation
        with torch.no_grad():  
            
            test_loss = 0          
            for bs, (x, y) in enumerate(test_loader):  
                x = x.to(device)
                y = y.to(device)

                y_pred = model(x)
                loss = loss_fn(y_pred, y)
                test_loss += loss.item()
            
            test_hist[epoch] = test_loss
        
        wdir = 'runs/train'
        if (epoch + 1) % opt.save_period == 0:             
            print(f'Epoch {epoch + 1} train loss: {train_loss} test loss: {test_loss}')           
            torch.save(model.state_dict(), os.path.join(wdir, str(epoch + 1) + '_epochs.pt'))        
        

    plt.figure(figsize=(30, 40))
    plt.plot(train_hist, label='Training Loss')
    plt.plot(test_hist, label='Test Loss')
    plt.legend()
    # plt.savefig(os.path.join('runs', 'train', 'loss.png'))
    plt.show()
    plt.cla()


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, help='path to the input data')    
    parser.add_argument('--device', type=str, help='cpu or cuda:0')
    parser.add_argument('--epochs', type=int, default=300)
    parser.add_argument('--batch_size', type=int)
    parser.add_argument('--split_ratio', type=float, default=0.2, help='split ratio between train data and test data')
    parser.add_argument('--seq_len', type=int, default=10, help='sequence length to make a prediction')
    parser.add_argument('--project', type=str, default='runs/train', help='save to project/name')
    parser.add_argument('--save_period', type=int, default=10, help="log model after every 'save_period' epochs")
    opt = parser.parse_args()
    train(opt)
