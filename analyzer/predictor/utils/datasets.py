import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from utils.preprocessor import csv_to_pd


def create_dataloader(data_path, is_train, scaler, batch_size, window_size, ahead):
    
    df = csv_to_pd(data_path)    
    print(f'df.shape: {df.shape}')    
    print(df.describe())
    outbreaks = np.array(df[:])    
    
    if is_train:        
        outbreaks = outbreaks.reshape(-1)  # reshape 2d matrix to 1d vector for MinMaxScaler().transform
        
        scaler = MinMaxScaler()
        scaler = scaler.fit(np.expand_dims(outbreaks, axis=1))  # np.expand_dims(data, axis=1).shape = (data_len, 1)
        scaled_outbreaks = scaler.transform(np.expand_dims(outbreaks, axis=1))  # normalize data between 0 and 1            
        scaled_outbreaks = scaled_outbreaks.reshape(-1, df.shape[-1])  # reshape 1d vector back to 2d matrix        
        print(f'boundary_check: {boundary_check(scaled_outbreaks)}')
        scaled_outbreaks = torch.from_numpy(scaled_outbreaks).float() # numpy default float64 -> torch default float32
        
        dataset = OIEDataset(scaled_outbreaks, window_size, ahead)            
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        return df, dataloader, scaler
        
    else:            
        outbreaks = outbreaks.reshape(-1)
        
        scaled_outbreaks = scaler.transform(np.expand_dims(outbreaks, axis=1))
        scaled_outbreaks = scaled_outbreaks.reshape(-1, df.shape[-1])       
        print(f'boundary_check: {boundary_check(scaled_outbreaks)}')
        scaled_outbreaks = torch.from_numpy(scaled_outbreaks).float() # numpy default float64 -> torch default float32
        
        dataset = OIEDataset(scaled_outbreaks, window_size, ahead)  
        dataloader = DataLoader(dataset, batch_size=batch_size)
        return df, dataloader


def boundary_check(x):    
    return np.any(x > 1.0), np.any(x < 0), np.any(np.isnan(x))


class OIEDataset(Dataset):
    
    def __init__ (self, data, window_size, ahead):                
        
        self.data = data
        self.window_size = window_size
        self.x, self.y = create_sequences(self.data, self.window_size, ahead)

    def __len__(self):
        return len(self.x)

    def __getitem__(self, index):
        return self.x[index], self.y[index]
        

def create_sequences(data, window_size, ahead):
    xs = []
    ys = []

    for i in range(len(data) - window_size - ahead):
        x = data[i:(i + window_size)]
        y = data[(i + window_size):(i + window_size + ahead)]
        # y = data[i + window_size]
        xs.append(x)
        ys.append(y)
    
    # torch.stack(xs).shape = ((data_len - window_size - 1), window_size, n_features)  ex) (1341, 10, 4)
    # torch.stack(ys).shape = ((data_len - window_size - 1), ahead, n_features)  ex) (1341, 2, 4)    
    return torch.stack(xs), torch.stack(ys)


