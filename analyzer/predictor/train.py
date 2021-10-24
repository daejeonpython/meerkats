import os
import math
import argparse
import easydict
import numpy as np
import matplotlib.pyplot as plt

import torch
from torch.optim import lr_scheduler
from utils.datasets import create_dataloader
from models.transformer import transformer


def train(opt):
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    epochs = opt.epochs
    window_size = opt.window_size    
    ahead = opt.ahead

    df, train_loader, scaler = create_dataloader(opt.train_data, is_train=True, scaler=None, batch_size=opt.batch_size, window_size=window_size, ahead=ahead)
    _, val_loader = create_dataloader(opt.validation_data, is_train=False, scaler=scaler, batch_size=opt.batch_size, window_size=window_size, ahead=ahead)


    # define transformer model hyperparameters
    model_args = easydict.EasyDict({
        'output_size': df.shape[-1],
        'window_size': window_size,
        'ahead': ahead,
        'batch_size': opt.batch_size,
        'lr': 1e-3,
        'e_features': df.shape[-1],
        'd_features': df.shape[-1],
        'd_hidn': 512,
        'n_head': 8,
        'd_head': 32,
        'dropout': 0.2,
        'd_ff': 256,
        'n_layer': 3,
        'dense_h': 256,
        'epochs': epochs,
        'device': device
    })
    
    model = transformer(model_args).to(device)
    print(model)        
    
    lr = model_args.lr
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, betas=(0.9, 0.999), eps=1e-08, weight_decay=1e-3)
    loss_fn = torch.nn.MSELoss()    
    scheduler = lr_scheduler.CosineAnnealingLR(optimizer, T_max=200, eta_min=0, last_epoch=-1)    
    
    best = {'loss': math.inf}
    train_hist = np.zeros(epochs)
    validation_hist = np.zeros(epochs)
    
    for epoch in range(epochs):

        # train
        model.train()
        train_loss = 0
        for bs, (x, y) in enumerate(train_loader):            
            optimizer.zero_grad()
            x = x.to(device)  # (batch_size, window_size, n_features)  ex) (128, 10, 4)
            y = y.to(device)  # (batch_size, ahead, n_features)  ex) (128, 2, 4)
            y_pred = model(x, x)
            loss = loss_fn(y_pred, y)
            loss.backward()         
            train_loss += loss.item()
            optimizer.step()
            
        train_hist[epoch] = train_loss

        # validation        
        with torch.no_grad():
            model.eval()
            validation_loss = 0
            for bs, (x, y) in enumerate(val_loader):  
                x = x.to(device)
                y = y.to(device)
                y_pred = model(x, x)
                loss = loss_fn(y_pred, y)
                validation_loss += loss.item()
            
            validation_hist[epoch] = validation_loss

        scheduler.step()

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
                        'output_size': model_args.output_size,
                        'window_size': model_args.window_size,
                        'ahead': model_args.ahead,
                        'e_features': model_args.e_features,
                        'd_features': model_args.d_features,
                        'd_hidn': model_args.d_hidn,
                        'n_head': model_args.n_head,
                        'd_head': model_args.d_head,
                        'dropout': model_args.dropout,
                        'd_ff': model_args.d_ff,
                        'n_layer': model_args.n_layer,
                        'dense_h': model_args.dense_h,
                    },
                    f,
                )    
        
    plt.figure(figsize=(16, 4))
    plt.title('Training Loss Graph')
    plt.xlabel('epochs')
    plt.ylabel('loss')
    plt.plot(train_hist[5:], label='Training Loss')
    plt.plot(validation_hist[5:], label='Validation Loss')
    plt.legend()
    plt.savefig(os.path.join('runs', 'loss.png'))
    plt.show()    


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--train_data', type=str, default='data/train/train.csv', help='path to the train data')    
    parser.add_argument('--validation_data', type=str, default='data/val/val.csv', help='path to the validation data')        
    parser.add_argument('--epochs', type=int, help='number of epochs')
    parser.add_argument('--batch_size', type=int, help='batch size')    
    parser.add_argument('--window_size', type=int, default=10, help='sequence length to make a prediction')    
    parser.add_argument('--ahead', type=int, default=1, help='prediction distance')      
    opt = parser.parse_args()

    train(opt)
